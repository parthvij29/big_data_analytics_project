const $ = id => document.getElementById(id);
const cityNames = "Delhi|New Delhi|Greater Noida|Noida|Gurugram|Faridabad|Ghaziabad|Mumbai|Pune|Nagpur|Nashik|Thane|Navi Mumbai|Chhatrapati Sambhajinagar|Bengaluru|Mysuru|Mangaluru|Hubballi|Chennai|Coimbatore|Madurai|Tiruchirappalli|Salem|Hyderabad|Warangal|Vijayawada|Visakhapatnam|Tirupati|Kochi|Thiruvananthapuram|Kozhikode|Kolkata|Howrah|Siliguri|Ahmedabad|Surat|Vadodara|Rajkot|Gandhinagar|Jaipur|Udaipur|Jodhpur|Kota|Ajmer|Lucknow|Agra|Kanpur|Varanasi|Prayagraj|Meerut|Chandigarh|Ludhiana|Amritsar|Dehradun|Shimla|Jammu|Srinagar|Bhopal|Indore|Gwalior|Jabalpur|Patna|Ranchi|Jamshedpur|Bhubaneswar|Cuttack|Raipur|Guwahati|Shillong|Imphal|Agartala|Gangtok|Panaji|Puducherry";
const carNames = "Tata Nexon EV|Tata Tiago EV|Tata Tigor EV|Tata Punch EV|Tata Curvv EV|Tata Harrier EV|MG ZS EV|MG Comet EV|MG Windsor EV|Mahindra XUV400|Mahindra BE 6|Mahindra XEV 9e|Hyundai IONIQ 5|Hyundai Kona Electric|Hyundai Creta Electric|Kia EV6|Kia EV9|Kia Carens Clavis EV|BYD Atto 3|BYD Seal|BYD Sealion 7|BYD eMAX 7|Citroën ë-C3|BMW i4|BMW iX|BMW iX1|BMW i7|Mercedes-Benz EQA|Mercedes-Benz EQB|Mercedes-Benz EQE SUV|Mercedes-Benz EQS|Volvo EX40|Volvo EC40|Audi Q8 e-tron|Porsche Taycan|Porsche Macan Electric|Tesla Model Y|MINI Countryman Electric";
for (const [id, names] of [['cities',cityNames],['cars',carNames]]) {
  for (const name of names.split('|')) $(id).append(new Option(name,name));
}
function navigate() {
  const pages = [...document.querySelectorAll('main > section')];
  const page = pages.find(p => p.id === location.hash.slice(1)) || $('home');
  for (const p of pages) p.hidden = p !== page;
  document.title = page.querySelector('h1').textContent + ' · VoltPulse';
  window.scrollTo(0,0);
}
window.addEventListener('hashchange',navigate);
navigate();
function el(tag, value) {
  const node = document.createElement(tag);
  node.textContent = value;
  return node;
}
function link(title,url) {
  const a = el('a',title);
  a.href = url;
  a.target = '_blank';
  a.rel = 'noopener';
  return a;
}
async function json(url) {
  const r = await fetch(url,{signal:AbortSignal.timeout(30000)});
  if (!r.ok) throw Error('The data provider is unavailable. Please try again.');
  return r.json();
}
async function city(name) {
  const params = new URLSearchParams({name:name.trim(),count:10,countryCode:'IN',language:'en'});
  const data = await json('https://geocoding-api.open-meteo.com/v1/search?' + params);
  const place = data.results?.find(p=>p.country_code==='IN');
  if (!place) throw Error('No Indian city match for ' + name + '. Try another spelling.');
  return {lat:place.latitude,lon:place.longitude,name:[place.name,place.admin1].filter(Boolean).join(', ')};
}
function km(a,b) {
  const rad = n=>n*Math.PI/180;
  const h = Math.sin(rad(b.lat-a.lat)/2)**2 + Math.cos(rad(a.lat))*Math.cos(rad(b.lat))*Math.sin(rad(b.lon-a.lon)/2)**2;
  return 12742*Math.asin(Math.sqrt(Math.min(1,h)));
}
function directions(origin,destination) {
  const params = new URLSearchParams({api:1,origin:origin.lat+','+origin.lon,destination:destination.lat+','+destination.lon,travelmode:'driving'});
  return 'https://www.google.com/maps/dir/?'+params;
}
async function stations(point,box) {
  if(!window.stationDirectory) throw Error('The station directory could not load. Reload the page to retry.');
  const sites=window.stationDirectory.filter(site=>km(point,site)<=15);
  sites.sort((a,b)=>km(point,a)-km(point,b));
  box.replaceChildren(el('p',sites.length+' mapped sites within 15 km of '+point.name+'. Distances are straight-line estimates.'));
  const map=mapPanel(box);
  if(map){
    map.setView([point.lat,point.lon],12);
    for(const site of sites){
      L.circleMarker([site.lat,site.lon],{radius:6,color:'#484391'}).bindPopup(el('strong',site.tags?.name || 'Charging station')).addTo(map);
    }
  }
  const list = el('ol','');
  for (const site of sites) {
    const tags = site.tags || {};
    const li = el('li','');
    li.append(el('strong',tags.name || tags.operator || 'Mapped charging station'), ' · '+km(point,site).toFixed(1)+' km');
    if(site.address) li.append(el('div',site.address));
    for(const [connector,power,quantity] of site.connections){
      li.append(el('div',[connector,power && power+' kW',quantity && quantity+' listed'].filter(Boolean).join(' / ')));
    }
    const rated=site.connections.filter(c=>Number(c[1])>0);
    if(box.closest('#driver') && rated.length){
      const select=el('select','');
      select.setAttribute('aria-label','Connector for charging estimate');
      for(const [type,power] of rated) select.add(new Option((type || 'Connector')+' / '+power+' kW',power));
      const use=el('button','Estimate this charge');
      use.onclick=()=>{
        const field=$('charge').elements.power;
        field.value=select.value;
        $('charge').closest('details').open=true;
        field.closest('details').open=true;
        field.focus();
      };
      const controls=el('div','');controls.className='station-actions';controls.append(select,use);li.append(controls);
    }
    if(site.verified) li.append(el('div','Record last verified: '+site.verified));
    if (bayTotal(site)) li.append(el('p',bayTotal(site)));
    const go=el('button','Get directions');
    go.onclick=()=>window.open(directions(point,site),'_blank','noopener');
    li.append(go);
    list.append(li);
  }
  box.append(list);
}
function failure(err) {
  return ['TypeError','TimeoutError','AbortError'].includes(err.name) ? 'Could not reach the data provider. Please try again.' : err.message;
}
for (const id of ['driverSearch','municipalSearch']) {
  const host = $(id);
  host.innerHTML = '<form><label>Indian city<input name="city" list="cities" placeholder="e.g. Jaipur" required></label><button>Find stations</button><button type="button">Use my location</button></form><div aria-live="polite"></div>';
  const form = host.querySelector('form'), box = host.lastElementChild;
  async function search(gps) {
    const buttons = [...form.querySelectorAll('button')];
    buttons.forEach(b=>b.disabled=true);
    box.textContent='Finding mapped stations…';
    try {
      const point = gps ? await new Promise((resolve,reject)=>navigator.geolocation.getCurrentPosition(p=>resolve({lat:p.coords.latitude,lon:p.coords.longitude,name:'your location'}),()=>reject(Error('Location unavailable. Search by city instead.')),{timeout:12000})) : await city(form.elements.city.value);
      await stations(point,box);
    } catch(err) {box.textContent=failure(err);}
    finally {buttons.forEach(b=>b.disabled=false);}
  }
  form.onsubmit = e=>{e.preventDefault();search(false);};
  form.lastElementChild.onclick=()=>search(true);
}
﻿function bayTotal(site) {
  const total = Number(site.points);
  return total > 0 ? 'Total charging points: '+total : '';
}
// Planning assumptions for a representative variant, editable for each trip.
function assumptions(model) {
  const packs = {'MG ZS EV':50.3,'Tata Tiago EV':24,'MG Comet EV':17.3,'Hyundai IONIQ 5':72.6,'Mahindra XUV400':39.4,'Tata Nexon EV':40.5};
  const battery = packs[model.trim()] || 45;
  return {battery,range:Math.round(battery/0.16),power:30,price:15,tariff:15,consumption:16};
}
for(const form of [$('charge'),$('route')]){
  const refresh=()=>{
    const values=assumptions(form.elements.vehicle.value);
    for(const [name,value] of Object.entries(values)){
      const field=form.elements[name];
      if(field) field.placeholder=value;
    }
  };
  form.elements.vehicle.addEventListener('input',refresh);
  refresh();
}
function estimateValue(fields,name){
  return Number(fields[name].value || assumptions(fields.vehicle.value)[name]);
}
$('charge').onsubmit=e=>{
  e.preventDefault();
  const f=e.target.elements;
  const capacity=estimateValue(f,'battery'),power=estimateValue(f,'power'),price=estimateValue(f,'price');
  const energy=capacity*(Number(f.end.value)-Number(f.start.value))/100;
  $('chargeResult').textContent=energy<=0?'Choose a target above your current charge.':
    Math.ceil(60*energy/power)+' min · ₹'+Math.round(energy*price)+' for '+energy.toFixed(1)+' kWh. Estimated using '+capacity+' kWh battery, '+power+' kW average power and ₹'+price+'/kWh. Excludes losses and fees.';
};
async function drive(points){
  const coords=points.map(p=>p.lon+','+p.lat).join(';');
  const data=await json('https://router.project-osrm.org/route/v1/driving/'+coords+'?overview=full&geometries=geojson');
  if(!data.routes?.length) throw Error('No road route found.');
  return data.routes[0];
}
function routeStations(road){
  const coords=road.geometry.coordinates;
  const samples=[];
  let distance=0,last=-Infinity,previous;
  for(const [lon,lat] of coords){
    const point={lon,lat};
    if(previous) distance+=km(previous,point);
    previous=point;
    if(distance-last<2) continue;
    samples.push({...point,distance});last=distance;
  }
  const candidates=[];
  for(const site of window.stationDirectory){
    // Prefer car connectors and exclude private and restricted site categories.
    if(![1,4,5].includes(site.usage) || !site.connections.some(c=>/Type 2/.test(c[0]))) continue;
    let offset=Infinity,progress=0;
    for(const point of samples){
      if(Math.abs(point.lat-site.lat)>.6 || Math.abs(point.lon-site.lon)>.75) continue;
      const separation=km(point,site);
      if(separation<offset){offset=separation;progress=point.distance;}
    }
    if(offset<60) candidates.push({site,progress:distance ? progress*road.distance/1000/distance : 0,offset});
  }
  return candidates.sort((a,b)=>a.progress-b.progress);
}

// Minimise the number of legs first, then the detour among equal-length plans.
function fewestStops(nodes,budget,measured){
  const paths=nodes.map(()=>({legs:Infinity,detour:Infinity,previous:-1}));
  paths[0]={legs:0,detour:0,previous:-1};
  for(let to=1;to<nodes.length;to++){
    const b=nodes[to];
    for(let from=0;from<to;from++){
      const a=nodes[from],prev=paths[from];
      if(!Number.isFinite(prev.legs)) continue;
      const estimate=b.progress-a.progress+1.35*(a.offset+b.offset);
      const length=measured.get(from+','+to) ?? estimate;
      if(length>budget || km(a.site,b.site)>budget) continue;
      const legs=prev.legs+1,detour=prev.detour+b.offset;
      if(legs<paths[to].legs || (legs===paths[to].legs && detour<paths[to].detour)){
        paths[to]={legs,detour,previous:from};
      }
    }
  }
  const path=[];
  if(!Number.isFinite(paths.at(-1).legs)) return path;
  for(let i=nodes.length-1;i>=0;i=paths[i].previous) path.unshift(i);
  return path;
}
async function planStops(a,b,direct,candidates,budget){
  if(direct.distance/1000<=budget) return {road:direct,stops:[],complete:true};
  const nodes=[{site:a,progress:0,offset:0},...candidates,{site:b,progress:direct.distance/1000,offset:0}];
  const measured=new Map();
  for(let attempt=0;attempt<12;attempt++){
    const path=fewestStops(nodes,budget,measured);
    if(!path.length) break;
    const points=path.map(i=>nodes[i].site);
    const road=await drive(points);
    if(road.legs.length!==points.length-1) break;
    if(road.legs.every(leg=>leg.distance/1000<=budget)){
      return {road,stops:points.slice(1,-1),complete:true};
    }
    road.legs.forEach((leg,i)=>measured.set(path[i]+','+path[i+1],leg.distance/1000));
  }
  return {road:direct,stops:[],complete:false};
}
function moreStations(candidates,stops){
  const selected=new Set(stops.map(s=>s.id));
  const others=candidates.filter(c=>!selected.has(c.site.id));
  const details=el('details','');
  details.append(el('summary','View more options ('+others.length+')'));
  if(!others.length) return details;
  details.append(el('p','Other mapped car chargers within 60 km of the original driving corridor, in travel order. Distance from the route is straight-line.'));
  const list=el('ol','');
  for(const {site,offset,progress} of others){
    const row=el('li','');
    row.append(el('strong',site.tags.name),el('div',[site.address,'Near route km '+Math.round(progress),offset.toFixed(1)+' km off route',bayTotal(site)].filter(Boolean).join(' · ')));
    list.append(row);
  }
  details.append(list);
  return details;
}
$('route').onsubmit=async e=>{
  e.preventDefault();
  const f=e.target.elements,box=$('routeResult'),button=e.target.querySelector('button');
  button.disabled=true;box.textContent='Checking roads and charging stops…';
  try{
    const [a,b]=await Promise.all([city(f.origin.value),city(f.destination.value)]);
    if(km(a,b)<0.01) throw Error('Choose two different cities.');
    const range=estimateValue(f,'range'), budget=range*.9;
    const direct=await drive([a,b]);
    const candidates=routeStations(direct);
    const {road,stops,complete}=await planStops(a,b,direct,candidates,budget);
    const distance=road.distance/1000;
    const usage=estimateValue(f,'consumption'),tariff=estimateValue(f,'tariff');
    box.replaceChildren(el('h2',a.name+' → '+b.name),el('p',Math.round(distance)+' km · '+(road.duration/3600).toFixed(1)+' h driving · approx. ₹'+Math.round(distance*usage/100*tariff)+' in electricity'));
    box.append(el('h3',complete ? stops.length+' charging stops planned' : 'No complete charging plan verified for this range.'));
    let travelled=0;
    for(const [i,leg] of road.legs.entries()){
      travelled+=leg.distance/1000;
      if(i<stops.length){
        const site=stops[i];
        box.append(el('h3','Stop '+(i+1)+' · '+site.tags.name),el('p',[site.address,'Km '+Math.round(travelled),bayTotal(site)].filter(Boolean).join(' · ')));
      }
    }
    if(complete){
      const arrival=Math.round(100*(1-road.legs.at(-1).distance/1000/range));
      box.append(el('p',(stops.length?'Expected arrival charge: ':'No charging stop needed. Expected arrival charge: ')+arrival+'%.'));
      const url=new URL(directions(a,b));
      if(stops.length) url.searchParams.set('waypoints',stops.map(s=>s.lat+','+s.lon).join('|'));
      box.append(link('Navigate this drive',url.href));
    }
    box.append(el('p','Estimate assumes a full start and full recharge at stops, '+range+' km range, 10% reserve, '+usage+' kWh/100 km and ₹'+tariff+'/kWh. Check connector, access and availability before leaving.'));
    box.append(moreStations(candidates,stops));
    const map=mapPanel(box);
    if(map){
      const path=L.geoJSON(road.geometry,{style:{color:'#5043a0',weight:5}}).addTo(map);
      map.fitBounds(path.getBounds(),{padding:[18,18]});
      stops.forEach((s,i)=>L.marker([s.lat,s.lon]).bindTooltip(el('span','Stop '+(i+1)+' · '+s.tags.name)).addTo(map));
    }
  }catch(err){box.textContent=failure(err);}
  finally{button.disabled=false;}
};
function mapPanel(box){
  if(!window.L) return null;
  const container=el('div','');
  container.className='map';
  box.append(container);
  const map=L.map(container,{scrollWheelZoom:false});
  L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png',{
    attribution:'&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap contributors</a>'
  }).addTo(map);
  return map;
}

// National electricity balance: MW at peak, million kWh across the financial year.
const powerHistory = [
  {year:'2021–22',peak:203014,met:200539,required:1379812,supplied:1374024},
  {year:'2022–23',peak:215888,met:207231,required:1513497,supplied:1505914},
  {year:'2023–24',peak:243271,met:239931,required:1626132,supplied:1622020},
  {year:'2024–25',peak:249856,met:249854,required:1693959,supplied:1692369}
];
const numberIN = new Intl.NumberFormat('en-IN',{maximumFractionDigits:2});
for (const year of powerHistory) $('gridYear').add(new Option(year.year));
$('gridYear').selectedIndex=powerHistory.length-1;
function showGridYear(){
  const year=powerHistory[$('gridYear').selectedIndex];
  const metrics=$('gridMetrics');
  metrics.replaceChildren();
  for(const [label,value,unit] of [
    ['Peak demand',year.peak,'MW'],['Peak met',year.met,'MW'],['Peak shortfall',year.peak-year.met,'MW'],
    ['Energy required',year.required,'MU'],['Energy supplied',year.supplied,'MU']
  ]){
    const cell=el('p',label);
    cell.append(el('strong',numberIN.format(value)+' '+unit));
    metrics.append(cell);
  }
  const history=$('gridHistory');
  history.replaceChildren(el('h3','Peak demand by year'));
  for(const entry of powerHistory){
    const row=el('div','');row.className='demand-row';
    const bar=el('meter','');bar.max=260000;bar.value=entry.peak;bar.setAttribute('aria-label','Peak demand in MW, '+entry.year);
    row.append(el('span',entry.year),bar,el('span',numberIN.format(entry.peak)+' MW'));history.append(row);
  }
}
$('gridYear').onchange=showGridYear;
showGridYear();

const directory=window.stationDirectory || [];
function gridStationOptions(){
  const term=$('gridSearch').value.trim().toLowerCase();
  const words=term.split(/\s+/).filter(Boolean);
  const matches=directory.filter(site=>{
    const tokens=((site.tags.name || '')+' '+site.address).toLowerCase().split(/[^\p{L}\p{N}]+/u);
    return words.every(word=>tokens.includes(word));
  });
  const menu=$('gridSite');
  menu.replaceChildren(new Option('Example site',''));
  for(const site of matches.slice(0,100)) menu.add(new Option(site.tags.name+' · '+site.address,site.id));
  if(term && matches.length) menu.selectedIndex=1;
  selectGridStation();
  if(term && !matches.length) $('gridSiteInfo').textContent='No directory match. Edit the example inputs below.';
}
function selectGridStation(){
  const site=directory.find(s=>String(s.id)===$('gridSite').value);
  const f=$('shift').elements;
  const ratings=site?.connections.map(c=>Number(c[1])).filter(n=>n>0) || [];
  f.power.value=ratings.length?Math.max(...ratings):50;
  f.ports.value=site?.points>0?site.points:4;
  $('gridSiteInfo').textContent=site?
    (ratings.length?'Highest listed connector rating used as the initial power estimate. ':'Charger rating unreported; example draw is 50 kW. ')+(site.points>0?'Directory lists '+site.points+' charging points.':'Point count unreported; example uses four.')+' Site limit and background load are editable assumptions.':
    'Example inputs. Replace with your site limit, measured background load and charger draw.';
  updateShift();
}
function updateShift(){
  const form=$('shift'), out=$('shiftResult');
  if(!form.checkValidity()){out.textContent='Enter valid values in all six fields to calculate the plan.';return;}
  const f=form.elements, limit=+f.limit.value, base=+f.base.value, power=+f.power.value, count=+f.count.value;
  const ports=+f.ports.value, minutes=+f.minutes.value;
  const proposed=base+Math.min(ports,count)*power;
  const simultaneous=Math.max(0,Math.min(ports,count,Math.floor((limit-base)/power+1e-10)));
  out.replaceChildren(el('h3',simultaneous?'Charge up to '+simultaneous+' at once':'No charging slot fits this limit'));
  out.append(el('p','Starting every available point with a waiting vehicle draws '+numberIN.format(proposed)+' kW, '+numberIN.format(Math.abs(limit-proposed))+' kW '+(proposed>limit?'above':'below')+' the limit.'));
  if(!simultaneous){out.append(el('p','Reduce the existing load or charger draw, or choose another charging window.'));return;}
  const batches=Math.ceil(count/simultaneous);
  out.append(el('p',batches+' charging '+(batches===1?'wave':'waves')+' · '+numberIN.format(batches*minutes)+' minutes to finish · '+numberIN.format(base+simultaneous*power)+' kW planned peak.'));
  const list=el('ol','');
  for(let i=0;i<Math.min(batches,5);i++){
    list.append(el('li','Minute '+i*minutes+'–'+(i+1)*minutes+' · '+Math.min(simultaneous,count-i*simultaneous)+' vehicle(s)'));
  }
  if(batches>5)list.append(el('li',(batches-5)+' more waves at the same interval.'));
  out.append(list);
}
$('gridSearch').oninput=gridStationOptions;
$('gridSite').onchange=selectGridStation;
$('shift').oninput=updateShift;
$('shift').onsubmit=e=>e.preventDefault();
gridStationOptions();

(function initBigDataAnalytics() {
  const analytics = window.voltPulseAnalytics;
  if (!analytics) return;

  // 1. Driver: Congestion & Peak Hours check
  const congForm = $('congestionCheck');
  const congOut = $('congestionResult');
  if (congForm && congOut) {
    const hourSel = congForm.elements.hour;
    for (let h = 0; h < 24; h++) {
      const label = String(h).padStart(2, '0') + ':00 – ' + String(h).padStart(2, '0') + ':59';
      hourSel.add(new Option(label, h));
    }
    hourSel.value = String(new Date().getHours());
    function renderCongestion() {
      const h = Number(hourSel.value);
      const portType = congForm.elements.portType.value;
      const { highHours, moderateHours, accuracy, f1 } = analytics.congestionModel;
      let level = 'Low', cls = 'badge-low', advice = 'Off-peak window — chargers are generally free with minimal wait.';
      if (highHours.includes(h)) {
        level = 'High'; cls = 'badge-high'; advice = 'Peak commute window — expect waiting queues, especially on ' + portType + ' bays.';
      } else if (moderateHours.includes(h)) {
        level = 'Moderate'; cls = 'badge-mod'; advice = 'Midday demand — moderate bay occupancy expected.';
      }
      const sessions = analytics.hourlySessions[h] ?? 0;
      const energy = analytics.hourlyEnergyKwh[h] ?? 0;
      congOut.replaceChildren();
      const badge = el('span', level + ' congestion');
      badge.className = 'congestion-badge ' + cls;
      const summary = el('p', '');
      summary.append(badge, ' · ', advice);
      const stats = el('p', 'Simulated hour profile: ' + numberIN.format(sessions) + ' sessions (' + numberIN.format(energy) + ' kWh) · Model accuracy ' + (accuracy * 100).toFixed(1) + '% (F1 ' + f1 + ').');
      congOut.append(summary, stats);
    }
    congForm.onchange = renderCongestion;
    renderCongestion();
  }

  // 2. Grid: Live Stream Power & Overload Monitor (Live Apache Kafka + JSONL replay fallback)
  const streamMetrics = $('streamMetrics');
  const streamAlerts = $('streamAlerts');
  const streamLatest = $('streamLatest');
  const streamSource = $('streamSource');
  const streamProduce = $('streamProduce');
  const streamToggle = $('streamToggle');
  const streamRestart = $('streamRestart');
  if (streamMetrics && streamAlerts) {
    const events = analytics.streamEvents || [];
    const threshold = analytics.streamSummary.thresholdKw;
    let idx = 0, totalPower = 0, occCount = 0, alertList = [], paused = false, liveKafkaMode = false;

    function drawStreamUI(countLabel, powerSum, occVal, alertsArr, latestText) {
      streamMetrics.replaceChildren();
      for (const [label, val] of [
        [liveKafkaMode ? 'Kafka events received' : 'Events replayed', countLabel],
        ['Sum of event power', numberIN.format(powerSum) + ' kW'],
        ['Occupied event rows', String(occVal)],
        ['Alerts (> ' + threshold + ' kW)', String(alertsArr.length)]
      ]) {
        const cell = el('p', label);
        cell.append(el('strong', val));
        streamMetrics.append(cell);
      }
      if (streamLatest && latestText) streamLatest.textContent = latestText;
      streamAlerts.replaceChildren();
      for (const a of alertsArr) {
        streamAlerts.append(el('li', '[ALERT @ ' + a.t + '] High Draw Warning: ' + a.station + ' Port #' + a.port + ' drawing ' + a.kw + ' kW'));
      }
    }

    function renderFallbackState(evt) {
      const latestText = evt
        ? 'Latest packet [' + evt.t + ']: ' + evt.station + ' · Port #' + evt.port + ' (' + evt.type + ') · ' + (evt.occ ? evt.kw + ' kW · SoC ' + evt.soc + '%' : 'Idle (0 kW)')
        : 'Starting local JSONL replay…';
      drawStreamUI(idx + ' / ' + events.length, totalPower, occCount, alertList, latestText);
    }

    function resetStream() {
      idx = 0; totalPower = 0; occCount = 0; alertList = [];
      renderFallbackState(null);
    }

    function stepFallback() {
      if (paused || liveKafkaMode || !events.length) return;
      if (idx >= events.length) resetStream();
      const evt = events[idx++];
      totalPower += evt.kw;
      if (evt.occ) occCount++;
      if (evt.kw > threshold) alertList.push(evt);
      renderFallbackState(evt);
    }

    async function pollLiveKafka() {
      if (paused) return;
      try {
        const r = await fetch('/api/stream', { cache: 'no-store', signal: AbortSignal.timeout(2000) });
        if (!r.ok) throw new Error('HTTP ' + r.status);
        const data = await r.json();
        if (data.source === 'kafka') {
          liveKafkaMode = true;
          if (streamSource) {
            streamSource.textContent = 'Source: Live Apache Kafka broker (' + data.broker + ' · topic ' + data.topic + '), flagging readings above ' + threshold + ' kW.';
          }
          if (streamRestart) streamRestart.hidden = true;
          const e = data.latest_event;
          const latestText = e
            ? 'Live Kafka packet [' + String(e.timestamp || '').split(' ').pop() + ']: ' + e.station_name + ' · Port #' + e.port_number + ' (' + e.port_type + ') · ' + (e.is_occupied ? e.current_power_draw_kw + ' kW · SoC ' + e.battery_soc_pct + '%' : 'Idle (0 kW)')
            : 'Connected to live Kafka topic (' + data.topic + '). Click "Produce 10 Kafka events" or run kafka_producer.py.';
          drawStreamUI(String(data.events_count), data.total_power_kw, data.occupied_ports, data.alerts || [], latestText);
          return;
        }
      } catch {}
      if (liveKafkaMode) {
        liveKafkaMode = false;
        if (streamRestart) streamRestart.hidden = false;
      }
      if (streamSource) {
        streamSource.textContent = 'Kafka broker offline — showing local JSONL replay fallback (live_stream_buffer.jsonl).';
      }
    }

    if (streamProduce) {
      streamProduce.onclick = async () => {
        streamProduce.disabled = true;
        try {
          const r = await fetch('/api/stream/produce', { method: 'POST' });
          if (r.ok && streamLatest) streamLatest.textContent = 'Streaming 10 new Indian EV telemetry events to Kafka…';
        } catch {}
        setTimeout(() => { streamProduce.disabled = false; }, 3500);
      };
    }

    if (streamToggle) {
      streamToggle.onclick = () => {
        paused = !paused;
        streamToggle.textContent = paused ? 'Resume stream' : 'Pause stream';
      };
    }
    if (streamRestart) {
      streamRestart.onclick = () => {
        resetStream();
        if (paused) { paused = false; if (streamToggle) streamToggle.textContent = 'Pause stream'; }
      };
    }

    resetStream();
    pollLiveKafka();
    setInterval(pollLiveKafka, 600);
    setInterval(stepFallback, 450);
  }

  // 3. Grid: Hourly Load Profile
  const hourlyBars = $('hourlyBars');
  if (hourlyBars) {
    const maxKwh = Math.max(...analytics.hourlyEnergyKwh);
    hourlyBars.replaceChildren();
    for (let h = 0; h < 24; h++) {
      const kwh = analytics.hourlyEnergyKwh[h];
      const count = analytics.hourlySessions[h];
      const row = el('div', '');
      row.className = 'demand-row';
      const bar = el('meter', '');
      bar.max = maxKwh;
      bar.value = kwh;
      bar.setAttribute('aria-label', 'Energy at hour ' + h);
      row.append(
        el('span', String(h).padStart(2, '0') + ':00'),
        bar,
        el('span', numberIN.format(kwh) + ' kWh (' + count + ')')
      );
      hourlyBars.append(row);
    }
  }

  // 4. Municipal: K-Means Optimal Hub Siting (Delhi NCR benchmark + any Indian city)
  const hubMetrics = $('hubMetrics');
  const hubList = $('hubList');
  const hubMapHost = $('hubMap');
  const hubForm = $('hubForm');
  const hubReset = $('hubReset');
  const hubSummary = $('hubSummary');
  let hubMap = null;
  let hubLayer = null;
  let currentHubView = null;

  function sqDist(a, b) {
    return (a.lat - b.lat) ** 2 + (a.lon - b.lon) ** 2;
  }

  function runKMeans(points, k) {
    // Deterministic farthest-point initialization for repeatable cluster centroids
    const sorted = [...points].sort((a, b) => (a.lat - b.lat) || (a.lon - b.lon));
    const centroids = [{ lat: sorted[0].lat, lon: sorted[0].lon }];
    while (centroids.length < k) {
      let best = sorted[0], bestD = -1;
      for (const p of sorted) {
        const minD = Math.min(...centroids.map(c => sqDist(p, c)));
        if (minD > bestD) { bestD = minD; best = p; }
      }
      centroids.push({ lat: best.lat, lon: best.lon });
    }

    let assign = new Array(points.length).fill(0);
    for (let iter = 0; iter < 50; iter++) {
      let changed = false;
      for (let i = 0; i < points.length; i++) {
        let bestC = 0, bestD = Infinity;
        for (let c = 0; c < k; c++) {
          const d = sqDist(points[i], centroids[c]);
          if (d < bestD) { bestD = d; bestC = c; }
        }
        if (assign[i] !== bestC) { assign[i] = bestC; changed = true; }
      }
      const sums = Array.from({ length: k }, () => ({ lat: 0, lon: 0, n: 0 }));
      for (let i = 0; i < points.length; i++) {
        sums[assign[i]].lat += points[i].lat;
        sums[assign[i]].lon += points[i].lon;
        sums[assign[i]].n++;
      }
      for (let c = 0; c < k; c++) {
        if (sums[c].n > 0) {
          centroids[c] = { lat: sums[c].lat / sums[c].n, lon: sums[c].lon / sums[c].n, count: sums[c].n };
        } else {
          centroids[c].count = 0;
        }
      }
      if (!changed) break;
    }

    let inertia = 0;
    for (let i = 0; i < points.length; i++) inertia += sqDist(points[i], centroids[assign[i]]);

    let silSum = 0, silCount = 0;
    if (k > 1 && points.length > k) {
      for (let i = 0; i < points.length; i++) {
        const ci = assign[i];
        const clusterDist = Array.from({ length: k }, () => ({ sum: 0, n: 0 }));
        for (let j = 0; j < points.length; j++) {
          if (i === j) continue;
          const cj = assign[j];
          clusterDist[cj].sum += Math.sqrt(sqDist(points[i], points[j]));
          clusterDist[cj].n++;
        }
        if (clusterDist[ci].n === 0) continue;
        const a = clusterDist[ci].sum / clusterDist[ci].n;
        let b = Infinity;
        for (let c = 0; c < k; c++) {
          if (c !== ci && clusterDist[c].n > 0) b = Math.min(b, clusterDist[c].sum / clusterDist[c].n);
        }
        if (b < Infinity && Math.max(a, b) > 0) {
          silSum += (b - a) / Math.max(a, b);
          silCount++;
        }
      }
    }
    return {
      centroids: centroids.map((c, idx) => ({
        label: 'Recommended Hub ' + (idx + 1) + ' (' + (c.count || 0) + ' sites)',
        lat: c.lat,
        lon: c.lon
      })),
      inertia: Number(inertia.toFixed(4)),
      silhouette: silCount ? Number((silSum / silCount).toFixed(4)) : 0
    };
  }

  function drawHubMap() {
    if (!currentHubView || !hubMapHost || $('municipal').hidden || typeof L === 'undefined') return;
    if (!hubMap) {
      hubMap = mapPanel(hubMapHost);
      if (!hubMap) return;
      hubLayer = L.layerGroup().addTo(hubMap);
    }
    hubMap.invalidateSize();
    hubLayer.clearLayers();
    const bounds = [];
    for (const s of currentHubView.stations || []) {
      L.circleMarker([s.lat, s.lon], { radius: 5, color: '#484391', fillOpacity: 0.55, weight: 1 })
        .bindPopup('<strong>' + (s.tags?.name || 'Mapped station') + '</strong>')
        .addTo(hubLayer);
      bounds.push([s.lat, s.lon]);
    }
    for (const c of currentHubView.centroids) {
      L.circleMarker([c.lat, c.lon], { radius: 9, color: '#a62122', fillColor: '#ffd44e', fillOpacity: 0.95, weight: 2 })
        .bindPopup('<strong>' + c.label + '</strong><br>' + c.lat.toFixed(4) + ', ' + c.lon.toFixed(4))
        .addTo(hubLayer);
      bounds.push([c.lat, c.lon]);
    }
    if (bounds.length > 1) hubMap.fitBounds(bounds, { padding: [24, 24] });
    else if (bounds.length === 1) hubMap.setView(bounds[0], 12);
  }

  function showHubView(view) {
    currentHubView = view;
    if (hubSummary) hubSummary.textContent = view.summary;
    hubMetrics.replaceChildren();
    for (const [label, val] of view.metrics) {
      const cell = el('p', label);
      cell.append(el('strong', val));
      hubMetrics.append(cell);
    }
    hubList.replaceChildren();
    for (const c of view.centroids) {
      hubList.append(el('li', c.label + ' — (' + c.lat.toFixed(4) + ', ' + c.lon.toFixed(4) + ')'));
    }
    drawHubMap();
  }

  function showBenchmarkHubs() {
    const h = analytics.hubSiting;
    showHubView({
      summary: 'Saved Delhi NCR benchmark (K-Means on 5,000 simulated NCR sessions).',
      metrics: [
        ['K clusters', String(h.k)],
        ['Silhouette score', String(h.silhouette)],
        ['WSSSE inertia', String(h.inertia)]
      ],
      centroids: h.centroids,
      stations: []
    });
  }

  if (hubMetrics && hubList) {
    showBenchmarkHubs();
    window.addEventListener('hashchange', drawHubMap);

    if (hubReset) {
      hubReset.onclick = () => {
        if (hubForm) hubForm.elements.city.value = '';
        showBenchmarkHubs();
      };
    }

    if (hubForm) {
      hubForm.onsubmit = async e => {
        e.preventDefault();
        const cityQuery = hubForm.elements.city.value.trim();
        const reqK = Number(hubForm.elements.k.value) || 4;
        if (!cityQuery) { showBenchmarkHubs(); return; }
        const btn = hubForm.querySelector('button');
        btn.disabled = true;
        if (hubSummary) hubSummary.textContent = 'Clustering mapped stations for ' + cityQuery + '…';
        try {
          const dir = window.stationDirectory || [];
          let sites = [];
          let areaLabel = cityQuery;
          try {
            const pt = await city(cityQuery);
            areaLabel = pt.name;
            sites = dir.filter(s => km(pt, s) <= 25);
            if (sites.length < 4) sites = dir.filter(s => km(pt, s) <= 50);
          } catch {
            const q = cityQuery.toLowerCase();
            sites = dir.filter(s => ((s.address || '') + ' ' + (s.tags?.name || '')).toLowerCase().includes(q));
          }

          // Deduplicate coordinates just like train_all_models.py
          const seen = new Set();
          const uniquePts = [];
          for (const s of sites) {
            const key = s.lat.toFixed(5) + ',' + s.lon.toFixed(5);
            if (!seen.has(key)) {
              seen.add(key);
              uniquePts.push({ lat: s.lat, lon: s.lon });
            }
          }

          if (uniquePts.length < 2) {
            if (hubSummary) hubSummary.textContent = 'Found only ' + uniquePts.length + ' unique station coordinate(s) near ' + areaLabel + '. Need at least 2 stations to form clusters.';
            return;
          }

          const k = Math.min(reqK, uniquePts.length);
          const res = runKMeans(uniquePts, k);
          showHubView({
            summary: areaLabel + ': clustered ' + sites.length + ' mapped stations (' + uniquePts.length + ' unique locations) into ' + k + ' optimal hub zones.',
            metrics: [
              ['K clusters', String(k)],
              ['Mapped stations', String(sites.length)],
              ['Silhouette score', String(res.silhouette)],
              ['WSSSE inertia', String(res.inertia)]
            ],
            centroids: res.centroids,
            stations: sites
          });
        } finally {
          btn.disabled = false;
        }
      };
    }
  }

  // 5. Grid: Real Live Weather & Solar Grid Conditions (Open-Meteo API)
  const liveGridForm = $('liveGridForm');
  const liveGridStatus = $('liveGridStatus');
  const liveGridMetrics = $('liveGridMetrics');
  const liveGridHourly = $('liveGridHourly');
  if (liveGridForm && liveGridStatus && liveGridMetrics && liveGridHourly) {
    let liveLoadedOnce = false;
    async function fetchLiveGrid(cityName) {
      const btn = liveGridForm.querySelector('button');
      btn.disabled = true;
      liveGridStatus.textContent = 'Fetching real-time weather & solar telemetry for ' + cityName + '…';
      try {
        const pt = await city(cityName);
        const params = new URLSearchParams({
          latitude: pt.lat,
          longitude: pt.lon,
          current: 'temperature_2m,relative_humidity_2m,shortwave_radiation,wind_speed_10m',
          hourly: 'temperature_2m,shortwave_radiation',
          forecast_days: 2,
          timezone: 'Asia/Kolkata'
        });
        const apiUrl = 'https://api.open-meteo.com/v1/forecast?' + params;
        const apiLink = $('liveGridApiLink');
        if (apiLink) apiLink.href = apiUrl;
        const data = await json(apiUrl);
        const cur = data.current || {};
        const temp = cur.temperature_2m ?? 0;
        const hum = cur.relative_humidity_2m ?? 0;
        const solar = cur.shortwave_radiation ?? 0;
        const wind = cur.wind_speed_10m ?? 0;

        let advisory = 'Moderate ambient load.';
        if (temp >= 35) advisory = 'High thermal load (>=35 °C) — expect higher EV battery cooling & HVAC grid draw.';
        else if (solar >= 400) advisory = 'Strong daytime solar (' + Math.round(solar) + ' W/m²) — favourable for solar-assisted EV fast charging.';
        else if (solar < 20) advisory = 'Low/zero solar irradiance — charging demand relies fully on grid/storage supply.';

        liveGridStatus.textContent = pt.name + ' · Live API updated at ' + (cur.time ? cur.time.replace('T', ' ') + ' IST' : new Date().toLocaleTimeString()) + ' · ' + advisory;

        liveGridMetrics.replaceChildren();
        for (const [label, val] of [
          ['Temperature', numberIN.format(temp) + ' °C'],
          ['Humidity', numberIN.format(hum) + ' %'],
          ['Solar irradiance', numberIN.format(solar) + ' W/m²'],
          ['Wind speed', numberIN.format(wind) + ' km/h']
        ]) {
          const cell = el('p', label);
          cell.append(el('strong', val));
          liveGridMetrics.append(cell);
        }

        const times = data.hourly?.time || [];
        const hSolar = data.hourly?.shortwave_radiation || [];
        const hTemp = data.hourly?.temperature_2m || [];
        const nowIso = cur.time ? cur.time.slice(0, 13) : '';
        let startIdx = times.findIndex(t => t.startsWith(nowIso));
        if (startIdx < 0) startIdx = 0;
        const sliceTimes = times.slice(startIdx, startIdx + 12);
        const maxSolar = Math.max(100, ...sliceTimes.map((_, i) => hSolar[startIdx + i] || 0));

        liveGridHourly.replaceChildren(el('h3', 'Next 12 hours · Solar irradiance & temperature forecast'));
        for (let i = 0; i < sliceTimes.length; i++) {
          const tLabel = sliceTimes[i].slice(11, 16);
          const sVal = hSolar[startIdx + i] ?? 0;
          const tVal = hTemp[startIdx + i] ?? 0;
          const row = el('div', '');
          row.className = 'demand-row';
          const bar = el('meter', '');
          bar.max = maxSolar;
          bar.value = sVal;
          bar.setAttribute('aria-label', 'Solar irradiance at ' + tLabel);
          row.append(
            el('span', tLabel),
            bar,
            el('span', Math.round(sVal) + ' W/m² · ' + tVal + ' °C')
          );
          liveGridHourly.append(row);
        }
      } catch (err) {
        liveGridStatus.textContent = failure(err);
      } finally {
        btn.disabled = false;
      }
    }

    liveGridForm.onsubmit = e => {
      e.preventDefault();
      fetchLiveGrid(liveGridForm.elements.city.value);
    };

    function maybeLoadLiveGrid() {
      if (!liveLoadedOnce && !$('grid').hidden) {
        liveLoadedOnce = true;
        fetchLiveGrid(liveGridForm.elements.city.value || 'Noida');
      }
    }
    window.addEventListener('hashchange', maybeLoadLiveGrid);
    maybeLoadLiveGrid();
  }
})();
