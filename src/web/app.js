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
