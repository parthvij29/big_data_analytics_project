import fs from 'node:fs'
import path from 'node:path'
import zlib from 'node:zlib'

const read = p => fs.readFileSync(p, 'utf8')
const write = (p, data) => fs.writeFileSync(p, data)
const xml = value => String(value).replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;').replaceAll('"','&quot;')
const declaration = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
const relBase = 'http://schemas.openxmlformats.org/officeDocument/2006/relationships/'
const relations = entries => declaration + '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">' + entries.map(([id, type, target]) => '<Relationship Id="'+id+'" Type="'+(type.startsWith('http') ? type : relBase+type)+'" Target="'+target+'"/>').join('') + '</Relationships>'
const contentTypes = (entries, ext = []) => declaration + '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="xml" ContentType="application/xml"/>' + ext.map(([e,t])=>'<Default Extension="'+e+'" ContentType="'+t+'"/>').join('') + entries.map(([p,t])=>'<Override PartName="/'+p+'" ContentType="'+t+'"/>').join('') + '</Types>'

// Standard ZIP containers for Office Open XML.
function zip(files) {
  const chunks = [], central = []
  let offset = 0
  for (const [name, data] of Object.entries(files)) {
    const filename = Buffer.from(name)
    const raw = Buffer.from(data)
    const compressed = zlib.deflateRawSync(raw)
    const checksum = zlib.crc32(raw)
    const local = Buffer.alloc(30), index = Buffer.alloc(46)
    local.writeUInt32LE(0x04034b50); local.writeUInt16LE(20,4); local.writeUInt16LE(8,8)
    local.writeUInt32LE(checksum,14); local.writeUInt32LE(compressed.length,18); local.writeUInt32LE(raw.length,22); local.writeUInt16LE(filename.length,26)
    index.writeUInt32LE(0x02014b50); index.writeUInt16LE(20,4); index.writeUInt16LE(20,6); index.writeUInt16LE(8,10)
    index.writeUInt32LE(checksum,16); index.writeUInt32LE(compressed.length,20); index.writeUInt32LE(raw.length,24); index.writeUInt16LE(filename.length,28); index.writeUInt32LE(offset,42)
    chunks.push(local, filename, compressed); central.push(index, filename)
    offset += local.length + filename.length + compressed.length
  }
  const directory = Buffer.concat(central), end = Buffer.alloc(22)
  end.writeUInt32LE(0x06054b50); end.writeUInt16LE(central.length/2,8); end.writeUInt16LE(central.length/2,10)
  end.writeUInt32LE(directory.length,12); end.writeUInt32LE(offset,16)
  return Buffer.concat([...chunks, directory, end])
}

function csv(text) {
  const records = text.trim().split(/\r?\n/).map(line =>
    Array.from((line + ',').matchAll(/(?:"((?:[^"]|"")*)"|([^,]*)),/g), match =>
      match[1] === undefined ? match[2] : match[1].replaceAll('""','"')))
  const keys = records.shift()
  return records.map(values => Object.fromEntries(keys.map((key, index)=>[key, values[index]])))
}
const sessions = csv(read('data/processed/cleaned_sessions.csv'))
const scores = Object.values(JSON.parse(read('data/processed/model_metrics.json')))
const events = read('data/streaming/live_stream_buffer.jsonl').trim().split(/\r?\n/).map(JSON.parse)
const replay = {
  records: events.length,
  occupied: events.filter(e => e.is_occupied).length,
  total: events.reduce((sum,e)=>sum+Number(e.current_power_draw_kw),0).toFixed(2),
  alerts: events.filter(e=>e.current_power_draw_kw>45).length
}
const metrics = [
  ['GBT', 'Session energy', 'RMSE 8.0874 kWh / MAE 6.7507 kWh / R² 0.3332'],
  ['Random Forest', 'Session energy', 'RMSE 7.9241 kWh / MAE 6.6594 kWh / R² 0.3599'],
  ['Random Forest', 'Congestion proxy', 'Accuracy 0.9630 / weighted F1 0.9620'],
  ['Linear regression', 'Active duration', 'RMSE 23.9893 min / MAE 16.8761 min / R² 0.8237'],
  ['K-means', 'Coordinate groups', 'k = 4 / silhouette 0.4445 / inertia 0.0314']
]
const groups = Object.groupBy(sessions, row=>row.City)
const cityRows = Object.entries(groups).sort(([a],[b])=>a.localeCompare(b)).map(([name, rows])=>[
  name, rows.length, (rows.reduce((sum,r)=>sum+Number(r.Energy_kWh),0)/1000).toFixed(2),
  new Set(rows.map(r=>r.Station_Name)).size
])
const chapters = []
for (const line of read('evaluation/report-content.md').split(/\r?\n/)) {
  if (line.startsWith('# ')) chapters.push({ name: line.slice(2), pages: [] })
  else if (line.startsWith('## ')) chapters.at(-1).pages.push({ title: line.slice(3), paragraphs: [] })
  else if (line.trim()) chapters.at(-1).pages.at(-1).paragraphs.push(line)
}
const tables = {
  '1.7': [['Stakeholder','Question','Evidence'],['Driver','Where might I charge?','Directory details and routing'],['Operator','What does a session consume?','Analytical CSV and held-out errors'],['Planner','Where are stations concentrated?','Directory and coordinate groups']],
  '1.9': [['Objective','Deliverable'],['Preparation','Cleaned session table'],['Prediction','Regression and classification evidence'],['Location review','Directory and coordinate clusters'],['Decision support','Filterable evaluation dashboard']],
  '2.2': [['Input','Process','Output'],['Synthetic CSV','PySpark ETL / portable fallback','Cleaned session CSV'],['Cleaned CSV','Benchmark and BI','Metrics, charts and filterable view'],['Raw CSV','Native Spark MLlib','Console metrics'],['JSONL events','Replay aggregation','Power and occupancy summary'],['Station snapshot','Browser and external map services','Location and route views']],
  '2.5': [['Actor','Action','System response'],['Evaluator','Select a city and connector','Refresh filtered session KPIs and histogram'],['Driver','Inspect a charging station','Show directory attributes'],['Planner','Review model evidence','Show coordinate groups and caveats']],
  '2.7': [['Synthetic city','Sessions','Energy (MWh)','Stations'],...cityRows],
  '2.8': [['Derived field','Definition'],['Hour','Hour of recorded session start'],['DayOfWeek','Sunday 1 through Saturday 7'],['IsDCFC','1 when Port_Type is DC Fast'],['Congestion_Level','Three-level mapping from hour'],['Charging_Mins','Active charging duration in minutes']],
  '2.10': [['Experimental parameter','Benchmark setting'],['Holdout fraction','0.20'],['Random seed','42'],['Energy model trees','100 per ensemble'],['Coordinate clusters','4'],['Initialisations','10 for scikit-learn K-means']],
  '3.3': [['Module','Source path'],['ETL','src/etl/etl_pipeline.py'],['MLlib','src/models/train_pyspark_mllib.py'],['Benchmark','src/models/train_all_models.py'],['Replay','src/ingestion/spark_stream_consumer.py'],['Portal','src/web/index.html'],['Offline dashboard','evaluation/VoltPulse_BI.html']],
  '3.6': [['File type','Contents'],['CSV','Generated source and prepared sessions'],['JSON','Saved benchmark metrics'],['JSONL','Simulated replay events'],['JavaScript','Bundled directory snapshot']],
  '4.2': [['Replay output','Value'],['Events',replay.records],['Occupied event rows',replay.occupied],['Sum of event power values (kW)',replay.total],['Events over 45 kW',replay.alerts]],
  '4.3': [['Model','Target','Saved benchmark metrics'],...metrics],
  '4.5': [['Readout','GBT','Random Forest','Difference'],['RMSE (kWh)','8.0874','7.9241','0.1633'],['MAE (kWh)','6.7507','6.6594','0.0913'],['R²','0.3332','0.3599','0.0267']],
  '4.6': [['Cluster','Latitude','Longitude'],...scores[4].Recommended_Centroids_Lat_Lon.map(([lat,lon],i)=>[i+1,lat.toFixed(5),lon.toFixed(5)])],
  '5.3': [['Objective','Evidence status'],['Batch and model code','Included'],['Benchmark results','Five saved results'],['Native Spark execution','Verify on evaluation workstation'],['BI','Offline HTML dashboard'],['Dataset approval and Turnitin','Confirmation required']],
  '5.6': [['Goal','Prototype contribution','Future measurement'],['7 Affordable and Clean Energy','Charging-energy visibility','Energy and peak demand'],['11 Sustainable Cities and Communities','Station access exploration','Geographic charger coverage'],['13 Climate Action','Supports electrified trip planning','Net emissions with a defined baseline']]
}
const images = {
  '4.4': ['data/processed/plots/model_comparison_bar.png','Held-out energy RMSE for the two saved scikit-learn benchmarks.'],
  '4.7': ['data/processed/plots/hourly_load_profile.png','Saved hourly profile for the synthetic session experiment.'],
  '4.9': ['data/processed/plots/spatial_hub_centroids.png','Saved coordinate clustering and candidate centroids.']
}
if (fs.existsSync('evaluation/BI-screenshot.png')) {
  images['3.9'] = ['evaluation/BI-screenshot.png', 'Offline BI dashboard rendered in Chrome with the supplied data.']
}
if (fs.existsSync('evaluation/architecture-flow.png')) {
  images['2.5'] = ['evaluation/architecture-flow.png', 'Level 1 data flow for the session experiment and public directory.']
}
const mainTitle = 'VoltPulse'
const subtitle = 'EV Charging Analytics and Business Intelligence'
const references = [
  '[1] Z. J. Lee, T. Li and S. H. Low. ACN-Data: Analysis and Applications of an Open EV Charging Dataset. ACM e-Energy, 2019. doi.org/10.1145/3307772.3328313',
  '[2] Apache Software Foundation. MLlib Main Guide. spark.apache.org/docs/latest/ml-guide.html',
  '[3] Open Charge Map. India data export. github.com/openchargemap/ocm-export/tree/main/data/IN',
  '[4] United Nations. Sustainable Development Goals 7, 11 and 13. sdgs.un.org/goals'
]
const front = 4
let nextPage = 1
const contents = chapters.flatMap(chapter=>[
  [chapter.name, nextPage],
  ...chapter.pages.map(page=>[page.title,nextPage++])
])
const frontPages = [
  { title: mainTitle, paragraphs: ['Project Report on',subtitle,'Submitted in Big Data Analytics and Business Intelligence Course, CSET 371','Bachelor of Technology','Bennett University, Greater Noida','Parth Vij   S24CSU1616','Under the guidance of','Faculty name and designation to be confirmed','School of Computer Science Engineering and Technology'] },
  { title: 'Declaration and Plagiarism Report Certificate', paragraphs: ['Declaration','I declare that the sources of information, datasets and materials used in this report are acknowledged. Student signature and declaration are to be completed after reviewing the report and confirming authorship and permitted assistance.','Turnitin report certificate','Similarity index __________ %     AI writing score __________ %','Turnitin report and verified scores are pending.','Student name Parth Vij     Enrolment number S24CSU1616','Student signature ____________________     Date ____________________'] },
  { title: 'Teamwork and Collaboration', paragraphs: ['The supplied Milestone 1 report lists Parth Vij as the project contributor. The table records his stated responsibilities.'], rows: [['Student','Enrolment','Contribution'],['Parth Vij','S24CSU1616','System design, data pipeline, telemetry simulation, model evaluation, BI and project documentation']] },
  { title: 'Table of Contents', toc: contents }
]
const reportPages = chapters.flatMap(ch=>ch.pages.map((p,index)=>({
  ...p, chapter:index===0?ch.name:null, rows:tables[p.title.split(' ')[0]], figure:images[p.title.split(' ')[0]]
})))
reportPages.push(
  {title:'References', paragraphs:references},
  {title:'Appendix A Additional Screenshots and Result Images', paragraphs:['A.1 Hourly profile from the saved synthetic session experiment.'],figure:images['4.7']},
  {title:'Appendix A Model and Location Evidence', paragraphs:['A.2 Spatial clustering output from the supplied experiment.'],figure:images['4.9']},
  ...(fs.existsSync('evaluation/Portal-screenshot.png') ? [{
    title:'Appendix A VoltPulse Web Portal',
    paragraphs:['A.3 Browser screenshot of the locally served VoltPulse home page. The menu opens the commuter, grid and municipal planning workspaces.'],
    figure:['evaluation/Portal-screenshot.png','VoltPulse landing view captured during local testing.']
  }] : []),
  {title:'Appendix B Dataset and Demo Reproduction', paragraphs:[
    'Open evaluation/START_HERE.md for the live demo steps and the artifact inventory.',
    'Use the submitted CSV and JSONL snapshots to reproduce the experiment. Record the Spark version, processing branch, training output and source hash before replacing any benchmark evidence.',
    'Present formal Turnitin documentation separately when available.'
  ]}
)
const allPages = [...frontPages,...reportPages]

const docMime = 'application/vnd.openxmlformats-officedocument.wordprocessingml.'
const wp = (value, {size=24, bold=false, align='both', after=140, before=0, height=360}={}) =>
  '<w:p><w:pPr><w:spacing w:before="'+before+'" w:after="'+after+'" w:line="'+height+'" w:lineRule="auto"/><w:jc w:val="'+align+'"/></w:pPr><w:r><w:rPr><w:rFonts w:ascii="Times New Roman" w:hAnsi="Times New Roman"/><w:sz w:val="'+size+'"/>'+(bold?'<w:b/>':'')+'</w:rPr><w:t xml:space="preserve">'+xml(value)+'</w:t></w:r></w:p>'
function table(rows) {
  const width = Math.floor(9200/rows[0].length)
  return '<w:tbl><w:tblPr><w:tblW w:w="9200" w:type="dxa"/><w:tblBorders><w:top w:val="single" w:sz="4"/><w:left w:val="single" w:sz="4"/><w:bottom w:val="single" w:sz="4"/><w:right w:val="single" w:sz="4"/><w:insideH w:val="single" w:sz="4"/><w:insideV w:val="single" w:sz="4"/></w:tblBorders></w:tblPr><w:tblGrid>'+rows[0].map(()=>'<w:gridCol w:w="'+width+'"/>').join('')+'</w:tblGrid>'+rows.map((row,i)=>'<w:tr>'+row.map(v=>'<w:tc><w:tcPr><w:tcW w:w="'+width+'" w:type="dxa"/>'+(i===0?'<w:shd w:fill="E7EBF0"/>':'')+'</w:tcPr>'+wp(v,{size:21,bold:i===0,align:'left',after:70,height:280})+'</w:tc>').join('')+'</w:tr>').join('')+'</w:tbl>'
}
const docFiles = {}, docRels = [['footer','footer','footer1.xml']]
let drawingId=0
function picture(file) {
  const data=fs.readFileSync(file), id=++drawingId
  const ext=path.extname(file).slice(1)
  const png=ext==='png'
  const ratio=png ? data.readUInt32BE(20)/data.readUInt32BE(16) : 0.8
  const w=Math.min(5100000,Math.floor(2450000/ratio)), h=Math.round(w*ratio)
  docFiles['word/media/image'+id+'.'+ext]=data
  docRels.push(['img'+id,'image','media/image'+id+'.'+ext])
  return '<w:p><w:pPr><w:jc w:val="center"/></w:pPr><w:r><w:drawing><wp:inline><wp:extent cx="'+w+'" cy="'+h+'"/><wp:docPr id="'+id+'" name="Figure '+id+'"/><a:graphic><a:graphicData uri="http://schemas.openxmlformats.org/drawingml/2006/picture"><pic:pic><pic:nvPicPr><pic:cNvPr id="'+id+'" name="'+xml(path.basename(file))+'"/><pic:cNvPicPr/></pic:nvPicPr><pic:blipFill><a:blip r:embed="img'+id+'"/><a:stretch><a:fillRect/></a:stretch></pic:blipFill><pic:spPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="'+w+'" cy="'+h+'"/></a:xfrm><a:prstGeom prst="rect"><a:avLst/></a:prstGeom></pic:spPr></pic:pic></a:graphicData></a:graphic></wp:inline></w:drawing></w:r></w:p>'
}
const wns='http://schemas.openxmlformats.org/wordprocessingml/2006/main'
const ans='http://schemas.openxmlformats.org/drawingml/2006/main'
const rns='http://schemas.openxmlformats.org/officeDocument/2006/relationships'
const geometry='<w:pgSz w:w="12240" w:h="15840"/><w:pgMar w:top="1560" w:right="1320" w:bottom="1060" w:left="1240" w:header="720" w:footer="864" w:gutter="0"/>'
const body=allPages.map((page,index)=>{
  const start=index===0 ? '' : index===front ?
    '<w:p><w:pPr><w:sectPr><w:type w:val="nextPage"/>'+geometry+'</w:sectPr></w:pPr></w:p>' :
    '<w:p><w:pPr><w:spacing w:before="0" w:after="0" w:line="20" w:lineRule="exact"/></w:pPr><w:r><w:br w:type="page"/></w:r></w:p>'
  if(index===0) return wp('Project Report on',{size:29,align:'center',before:900,after:320}) +
    wp(mainTitle,{size:56,bold:true,align:'center',after:230}) + wp(subtitle,{size:34,bold:true,align:'center',after:680}) +
    page.paragraphs.slice(2,5).map(v=>wp(v,{align:'center'})).join('') +
    wp('By',{align:'center',before:370}) + wp(page.paragraphs[5],{align:'center',bold:true,after:450}) +
    (fs.existsSync('report/format_assets/word/media/image1.jpeg') ? picture('report/format_assets/word/media/image1.jpeg') : '') +
    page.paragraphs.slice(6).map(v=>wp(v,{align:'center'})).join('')
  const heading=(page.chapter?wp('Chapter '+page.chapter,{bold:true,size:33,align:'left',after:300}):'')+
    wp(page.title,{bold:true,size:28,align:'left',after:285})
  const toc=page.toc ? page.toc.map(([title,n])=>wp(title+'  ·  '+n,{size:19,align:'left',height:208,after:0})).join('') : ''
  return start+heading+(page.paragraphs||[]).map(v=>wp(v)).join('')+
    (page.rows?table(page.rows):'')+
    (page.figure?picture(page.figure[0])+wp(page.figure[1],{size:20,align:'center'}):'')+toc
}).join('')
docFiles['word/document.xml']=declaration+'<w:document xmlns:w="'+wns+'" xmlns:r="'+rns+'" xmlns:a="'+ans+'" xmlns:wp="http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing" xmlns:pic="http://schemas.openxmlformats.org/drawingml/2006/picture"><w:body>'+body+'<w:sectPr><w:footerReference w:type="default" r:id="footer"/>'+geometry+'<w:pgNumType w:start="1"/></w:sectPr></w:body></w:document>'
docFiles['word/footer1.xml']=declaration+'<w:ftr xmlns:w="'+wns+'"><w:p><w:pPr><w:jc w:val="center"/></w:pPr><w:fldSimple w:instr="PAGE"><w:r><w:t>1</w:t></w:r></w:fldSimple></w:p></w:ftr>'
docFiles['[Content_Types].xml']=contentTypes([['word/document.xml',docMime+'document.main+xml'],['word/footer1.xml',docMime+'footer+xml']],[['png','image/png'],['jpeg','image/jpeg']])
docFiles['_rels/.rels']=relations([['doc','officeDocument','word/document.xml']])
docFiles['word/_rels/document.xml.rels']=relations(docRels)
write('evaluation/VoltPulse_Final_Report.docx',zip(docFiles))

const bins=Object.entries(Object.groupBy(sessions,r=>r.City+' / '+r.Port_Type)).map(([key, rows])=>{
  const [city,port]=key.split(' / ')
  const hours=Array.from({length:24},()=>0)
  for(const row of rows) hours[Number(row.Hour)]++
  return {city,port,hours,count:rows.length,energy:rows.reduce((t,r)=>t+Number(r.Energy_kWh),0),duration:rows.reduce((t,r)=>t+Number(r.Charging_Mins),0)}
})
const dashboard=declaration.replace(/.*/,'<!doctype html>')+'<html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>VoltPulse experiment dashboard</title><style>'+
  '*{box-sizing:border-box}body{margin:0;background:#edf2f3;color:#142a35;font:16px system-ui}main{max-width:1120px;margin:auto;padding:44px 24px}h1{font-size:42px;margin:0}h2{margin:0 0 16px}p{line-height:1.5}.filters,.cards{display:flex;gap:16px;flex-wrap:wrap;margin:20px 0}.card,section{background:white;border:1px solid #d6e1e4;border-radius:12px;padding:20px}.card{flex:1;min-width:160px}.card strong{display:block;font-size:30px;margin-top:5px}section{margin:18px 0}select{display:block;margin-top:6px;font:inherit;padding:6px 12px}.chart{display:grid;grid-template-columns:repeat(24,minmax(8px,1fr));gap:5px;height:190px;align-items:end}.col{display:flex;flex-direction:column;justify-content:end;height:100%;text-align:center;font-size:11px}.bar{background:#006e70;display:block;margin-top:auto;border-radius:4px 4px 0 0}.scroll{overflow:auto}table{width:100%;border-collapse:collapse}th,td{text-align:left;padding:10px;border-bottom:1px solid #dbe4e5}.note{color:#405961}.skip{position:absolute;left:-9999px}.skip:focus{left:1rem}</style><main>'+
  '<h1>VoltPulse experiment dashboard</h1><p class="note">Synthetic Indian EV charging sessions and saved scikit-learn results</p>'+
  '<div class="filters"><label>City<select id="city"><option value="">All cities</option>'+cityRows.map(r=>'<option>'+xml(r[0])+'</option>').join('')+'</select></label><label>Connector<select id="port"><option value="">All connectors</option><option>DC Fast</option><option>Level 2</option></select></label></div>'+
  '<div class="cards" aria-live="polite"><div class="card">Sessions<strong id="count"></strong></div><div class="card">Energy delivered<strong id="energy"></strong></div><div class="card">Mean active duration<strong id="duration"></strong></div></div>'+
  '<section><h2>Sessions by start hour</h2><div id="chart" class="chart" role="img" aria-label="Hourly session count"></div><p id="hourSummary" class="note"></p></section>'+
  '<section><h2>Saved model scorecard</h2><div class="scroll"><table><thead><tr><th scope="col">Model</th><th scope="col">Target</th><th scope="col">Benchmark result</th></tr></thead><tbody>'+metrics.map(r=>'<tr>'+r.map(x=>'<td>'+xml(x)+'</td>').join('')+'</tr>').join('')+'</tbody></table></div><p class="note">The classifier learns hour-derived labels. The table shows global benchmark scores and stays fixed when you filter sessions.</p></section>'+
  '<section><h2>Simulated replay</h2><p>'+replay.records+' event rows, '+replay.occupied+' occupied rows, '+replay.alerts+' events above 45 kW. The sum of event power values was '+replay.total+' kW across the file.</p></section></main>'+
  '<script>const bins='+JSON.stringify(bins)+';const byId=id=>document.getElementById(id);function update(){const selected=bins.filter(b=>(!byId("city").value||b.city===byId("city").value)&&(!byId("port").value||b.port===byId("port").value));const counts=Array.from({length:24},(_,h)=>selected.reduce((t,r)=>t+r.hours[h],0));const count=selected.reduce((t,r)=>t+r.count,0);const energy=selected.reduce((t,r)=>t+r.energy,0);const duration=selected.reduce((t,r)=>t+r.duration,0);const max=Math.max(1,...counts);byId("count").textContent=count.toLocaleString("en-IN");byId("energy").textContent=(energy/1000).toFixed(2)+" MWh";byId("duration").textContent=count?(duration/count).toFixed(1)+" min":"—";byId("chart").innerHTML=counts.map((n,h)=>"<div class=col title=\\""+h+":00 — "+n+" sessions\\"><span class=bar style=\\"height:"+90*n/max+"%\\"></span>"+h+"</div>").join("");byId("hourSummary").textContent=count?"Busiest start hour: "+counts.indexOf(max)+":00 ("+max+" sessions).":"No sessions match the selection.";byId("chart").setAttribute("aria-label",counts.map((n,h)=>h+":00 "+n+" sessions").join(", "));}byId("city").addEventListener("change",update);byId("port").addEventListener("change",update);update();</script></html>'
write('evaluation/VoltPulse_BI.html',dashboard)
write('evaluation/replay-evidence.txt',
  'VoltPulse telemetry fixture review\nInput: data/streaming/live_stream_buffer.jsonl\n'+
  'Event rows: '+replay.records+'\nOccupied event rows: '+replay.occupied+'\nSum of event power values: '+replay.total+' kW\nEvents over 45 kW: '+replay.alerts+
  '\nMethod: independently aggregated by the evaluation artifact builder from the saved simulator output.\n')
const slides = [
  {title:'VoltPulse', lines:['EV Charging Analytics and Business Intelligence','Parth Vij  /  S24CSU1616','CSET 371  /  Bennett University']},
  {title:'Three decisions around EV charging',lines:['Driver: find a suitable charger and plan a trip within range.','Operator: compare session energy and active duration.','Planner: examine station coverage and identify where more evidence is needed.']},
  {title:'Where the data comes from',lines:['5,000 synthetic charging sessions across four Indian cities.','Open Charge Map India snapshot for the public station directory.','Separate simulated Boulder-labelled events for telemetry replay.','Published Indian electricity demand provides grid context.']},
  {title:'How VoltPulse processes the inputs',lines:['CSV sessions → PySpark ETL → prepared session data','Prepared data → scikit-learn benchmark → metrics and charts','Raw sessions → native Spark MLlib → terminal metrics','Station snapshot → web directory and planning controls']},
  {title:'Random Forest had lower session-energy error',lines:['Random Forest: 7.92 kWh RMSE and R² of 0.360.','Gradient boosting: 8.09 kWh RMSE and R² of 0.333.','Same held-out split. The RMSE difference was 0.16 kWh.','Saved scikit-learn results for simulated sessions.']},
  {title:'What the other three models show',lines:['Random Forest achieved 0.962 weighted F1 on hour-derived congestion labels.','Linear regression had a 16.88-minute MAE for active duration.','K-means grouped coordinates into four clusters with a silhouette of 0.445.','A centroid identifies a group of coordinates. Site feasibility requires more data.']},
  {title:'Live demonstration',lines:['Find a station and inspect its connector information.','Filter the experiment dashboard by city and connector.','Show the PySpark pipeline and its outputs if the local run is available.','Replay the saved simulated telemetry and explain the threshold.']},
  {title:'How the prototype relates to the SDGs',lines:['SDG 7 — Explore charging energy and future peak-demand management.','SDG 11 — Examine station access and support urban infrastructure planning.','SDG 13 — Support electrified trip planning. Emissions impact remains unmeasured.']},
  {title:'Project contribution',lines:['Parth Vij: system design, data preparation and telemetry simulation.','Model training and interpretation across five estimators.','Web interface, BI evidence and documentation.']},
  {title:'What we would validate next',lines:['Use faculty-approved measured sessions and hold out later dates and unseen stations.','Use observed queue or occupancy labels for congestion modelling.','Validate candidate sites with access, demand and grid-capacity evidence.','Capture native Spark metrics on the evaluation workstation.']}
]
const pns='http://schemas.openxmlformats.org/presentationml/2006/main'
const pptMime='application/vnd.openxmlformats-officedocument.presentationml.'
const ppt={}
const blankGroup='<p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr><p:grpSpPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="0" cy="0"/><a:chOff x="0" y="0"/><a:chExt cx="0" cy="0"/></a:xfrm></p:grpSpPr>'
const openTag=(tag,attrs='')=>declaration+'<p:'+tag+' xmlns:p="'+pns+'" xmlns:a="'+ans+'" xmlns:r="'+rns+'" '+attrs+'>'
const cm=value=>Math.round(value*360000)
function shape(id,name,value,x,y,w,h,font,color,bold=false){
  return '<p:sp><p:nvSpPr><p:cNvPr id="'+id+'" name="'+xml(name)+'"/><p:cNvSpPr txBox="1"/><p:nvPr/></p:nvSpPr><p:spPr><a:xfrm><a:off x="'+cm(x)+'" y="'+cm(y)+'"/><a:ext cx="'+cm(w)+'" cy="'+cm(h)+'"/></a:xfrm><a:prstGeom prst="rect"><a:avLst/></a:prstGeom><a:noFill/></p:spPr><p:txBody><a:bodyPr wrap="square" lIns="0" rIns="0" tIns="0" bIns="0"/><a:lstStyle/><a:p><a:r><a:rPr lang="en-US" sz="'+font+'"'+(bold?' b="1"':'')+'><a:solidFill><a:srgbClr val="'+color+'"/></a:solidFill><a:latin typeface="Aptos"/></a:rPr><a:t>'+xml(value)+'</a:t></a:r></a:p></p:txBody></p:sp>'
}
slides.forEach(({title,lines},i)=>{
  const cover=i===0
  const bg=cover?'11313D':'F6F9F9', dark=cover?'FFFFFF':'11313D'
  const text=cover?'DAEDEB':'29454C'
  const accent=cover?'93DFCA':'067467'
  const header=shape(2,'Heading',title,2.25,cover?4.05:2.2,29,3.2,cover?6500:3600,dark,true)
  const items=lines.map((line,j)=>shape(3+j,'Text '+(j+1),line,2.3,(cover?8.1:5.7)+j*2.55,28.5,2.4,cover?2600:2450,text)).join('')
  const folio=shape(10,'Slide number',cover?'MILESTONE 3':String(i+1).padStart(2,'0'),2.3,17.05,10,0.9,1300,accent,true)
  const n=i+1
  ppt['ppt/slides/slide'+n+'.xml']=openTag('sld')+'<p:cSld><p:bg><p:bgPr><a:solidFill><a:srgbClr val="'+bg+'"/></a:solidFill><a:effectLst/></p:bgPr></p:bg><p:spTree>'+blankGroup+header+items+folio+'</p:spTree></p:cSld><p:clrMapOvr><a:masterClrMapping/></p:clrMapOvr></p:sld>'
  ppt['ppt/slides/_rels/slide'+n+'.xml.rels']=relations([['layout','slideLayout','../slideLayouts/slideLayout1.xml']])
})
const slideLinks=slides.map((_,i)=>['slide'+(i+1),'slide','slides/slide'+(i+1)+'.xml'])
const colorMap='<p:clrMap accent1="accent1" accent2="accent2" accent3="accent3" accent4="accent4" accent5="accent5" accent6="accent6" bg1="lt1" bg2="lt2" folHlink="folHlink" hlink="hlink" tx1="dk1" tx2="dk2"/>'
ppt['ppt/presentation.xml']=openTag('presentation')+'<p:sldMasterIdLst><p:sldMasterId id="2147483648" r:id="master"/></p:sldMasterIdLst><p:sldIdLst>'+slideLinks.map(([id],i)=>'<p:sldId id="'+(256+i)+'" r:id="'+id+'"/>').join('')+'</p:sldIdLst><p:sldSz cx="12192000" cy="6858000" type="screen16x9"/><p:notesSz cx="6858000" cy="9144000"/></p:presentation>'
ppt['ppt/slideMasters/slideMaster1.xml']=openTag('sldMaster')+'<p:cSld><p:spTree>'+blankGroup+'</p:spTree></p:cSld>'+colorMap+'<p:sldLayoutIdLst><p:sldLayoutId id="2147483649" r:id="layout"/></p:sldLayoutIdLst><p:txStyles><p:titleStyle/><p:bodyStyle/><p:otherStyle/></p:txStyles></p:sldMaster>'
ppt['ppt/slideLayouts/slideLayout1.xml']=openTag('sldLayout','type="blank" preserve="1"')+'<p:cSld name="Blank"><p:spTree>'+blankGroup+'</p:spTree></p:cSld><p:clrMapOvr><a:masterClrMapping/></p:clrMapOvr></p:sldLayout>'
const defaultColors={dk1:'11313D',lt1:'FFFFFF',dk2:'29454C',lt2:'F6F9F9',accent1:'067467',accent2:'31867E',accent3:'93DFCA',accent4:'467790',accent5:'D99136',accent6:'A3B6B9',hlink:'0864AF',folHlink:'64477C'}
const schemeFill='<a:solidFill><a:schemeClr val="phClr"/></a:solidFill>'
const fontScheme=(tag)=>'<a:'+tag+'><a:latin typeface="Aptos"/><a:ea typeface=""/><a:cs typeface=""/></a:'+tag+'>'
ppt['ppt/theme/theme1.xml']=declaration+'<a:theme xmlns:a="'+ans+'" name="VoltPulse"><a:themeElements><a:clrScheme name="VoltPulse">'+
  Object.entries(defaultColors).map(([key,val])=>'<a:'+key+'><a:srgbClr val="'+val+'"/></a:'+key+'>').join('')+
  '</a:clrScheme><a:fontScheme name="Aptos">'+fontScheme('majorFont')+fontScheme('minorFont')+
  '</a:fontScheme><a:fmtScheme name="VoltPulse"><a:fillStyleLst>'+schemeFill.repeat(3)+
  '</a:fillStyleLst><a:lnStyleLst>'+[9525,25400,38100].map(w=>'<a:ln w="'+w+'">'+schemeFill+'<a:prstDash val="solid"/></a:ln>').join('')+
  '</a:lnStyleLst><a:effectStyleLst>'+('<a:effectStyle><a:effectLst/></a:effectStyle>').repeat(3)+
  '</a:effectStyleLst><a:bgFillStyleLst>'+schemeFill.repeat(3)+'</a:bgFillStyleLst></a:fmtScheme></a:themeElements></a:theme>'
ppt['ppt/slideMasters/_rels/slideMaster1.xml.rels']=relations([['layout','slideLayout','../slideLayouts/slideLayout1.xml'],['theme','theme','../theme/theme1.xml']])
ppt['ppt/slideLayouts/_rels/slideLayout1.xml.rels']=relations([['master','slideMaster','../slideMasters/slideMaster1.xml']])
ppt['ppt/_rels/presentation.xml.rels']=relations([['master','slideMaster','slideMasters/slideMaster1.xml'],...slideLinks])
ppt['_rels/.rels']=relations([['ppt','officeDocument','ppt/presentation.xml']])
ppt['[Content_Types].xml']=contentTypes([
  ['ppt/presentation.xml',pptMime+'presentation.main+xml'],
  ['ppt/slideLayouts/slideLayout1.xml',pptMime+'slideLayout+xml'],
  ['ppt/slideMasters/slideMaster1.xml',pptMime+'slideMaster+xml'],
  ['ppt/theme/theme1.xml','application/vnd.openxmlformats-officedocument.theme+xml'],
  ...slideLinks.map(([, , target])=>['ppt/'+target,pptMime+'slide+xml'])
])
write('evaluation/VoltPulse_Presentation.pptx',zip(ppt))
const deckHtml = '<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>VoltPulse presentation</title><style>body{margin:0;background:#11313d;color:#11313d;font:clamp(18px,2vw,32px) system-ui}article{background:#f6f9f9;min-height:100vh;padding:9vh 8vw;box-sizing:border-box}article:first-of-type{background:#11313d;color:white}article[hidden]{display:none}h1{font-size:1.9em;line-height:1.15;margin:0 0 1.2em}li{margin:.8em 0;line-height:1.4}button{font:inherit;padding:.3em .7em}nav{position:fixed;bottom:1.5vh;right:3vw}span{background:#fff;border-radius:.2em;padding:.33em}</style>'+
  slides.map((slide,i)=>'<article '+(i?'hidden':'')+'><h1>'+xml(slide.title)+'</h1><ul>'+slide.lines.map(line=>'<li>'+xml(line)+'</li>').join('')+'</ul></article>').join('')+
  '<nav><button id="back">Previous</button> <span id="page"></span> <button id="next">Next</button></nav><script>const slides=[...document.querySelectorAll("article")];let pos=0;function show(i){pos=Math.max(0,Math.min(i,slides.length-1));slides.forEach((slide,n)=>slide.hidden=n!==pos);document.getElementById("page").textContent=(pos+1)+" / "+slides.length;}document.getElementById("back").onclick=()=>show(pos-1);document.getElementById("next").onclick=()=>show(pos+1);document.addEventListener("keydown",e=>{if(e.key==="ArrowLeft")show(pos-1);if(e.key==="ArrowRight")show(pos+1)});show(0);</script></html>'
write('evaluation/VoltPulse_Presentation.html',deckHtml)

const printHead = '<!doctype html><html lang="en"><meta charset="utf-8"><title>VoltPulse Project Report</title><style>@page{size:letter;margin:1.083in .917in .736in .861in}body{margin:0;color:#111;font:12pt/1.5 "Times New Roman",serif}section{height:8.98in;position:relative;break-after:page;box-sizing:border-box;padding-bottom:32px}section:last-child{break-after:auto}h1{font-size:20pt;line-height:1.2;margin:0 0 16pt}h2{font-size:15pt;line-height:1.3;margin:0 0 15pt}p{text-align:justify;margin:0 0 10pt}footer{position:absolute;bottom:0;width:100%;text-align:center}table{width:100%;border-collapse:collapse;margin-top:20pt}td,th{border:1px solid #888;text-align:left;padding:5px 7px;font-size:11pt;vertical-align:top}th{background:#eef1f3}figure{text-align:center;margin:16pt 0}img{display:block;margin:auto;max-width:100%;max-height:2.65in}figcaption{font-size:10.5pt;margin-top:8px}.cover{text-align:center;padding-top:35pt}.cover h1{font-size:34pt;margin:16pt 0}.cover p{text-align:center}.cover img{max-height:1.18in;margin:18pt auto}.toc{width:100%;border:0;margin:0}.toc td{border:0;padding:0;font-size:8.5pt;line-height:1.12}.toc td:last-child{text-align:right}</style>'
const embedded = file => 'data:image/'+(file.endsWith('.png')?'png':'jpeg')+';base64,'+fs.readFileSync(file).toString('base64')
const reportHtml=printHead+allPages.map((page,i)=>{
  if(i===0) return '<section class="cover"><p>Project Report on</p><h1>VoltPulse</h1><h2>'+xml(subtitle)+'</h2>'+page.paragraphs.slice(2,5).map(v=>'<p>'+xml(v)+'</p>').join('')+'<p>By</p><p><strong>'+xml(page.paragraphs[5])+'</strong></p><img alt="Bennett University" src="'+embedded('report/format_assets/word/media/image1.jpeg')+'">'+page.paragraphs.slice(6).map(v=>'<p>'+xml(v)+'</p>').join('')+'</section>'
  const paragraph=(page.paragraphs||[]).map(v=>'<p>'+xml(v)+'</p>').join('')
  const rows=page.rows ? '<table>'+page.rows.map((row,n)=>'<tr>'+row.map(v=>'<'+(n?'td':'th')+'>'+xml(v)+'</'+(n?'td':'th')+'>').join('')+'</tr>').join('')+'</table>' : ''
  const figure=page.figure?'<figure><img alt="'+xml(page.figure[1])+'" src="'+embedded(page.figure[0])+'"><figcaption>'+xml(page.figure[1])+'</figcaption></figure>':''
  const toc=page.toc?'<table class="toc">'+page.toc.map(([v,n])=>'<tr><td>'+xml(v)+'</td><td>'+n+'</td></tr>').join('')+'</table>':''
  return '<section>'+(page.chapter?'<h1>Chapter '+xml(page.chapter)+'</h1>':'')+'<h2>'+xml(page.title)+'</h2>'+paragraph+rows+figure+toc+(i>=front?'<footer>'+(i-front+1)+'</footer>':'')+'</section>'
}).join('')+'</html>'
write('evaluation/VoltPulse_Report_Print.html',reportHtml)

if (process.argv.includes('--chart-pages')) {
  const out = process.env.TEMP
  const chart = (title, subtitle, body) => '<!doctype html><meta charset="utf-8"><style>body{margin:0;overflow:hidden;color:#132d39;background:white;font:19px system-ui}main{padding:30px 42px}h1{font-size:30px;margin:0 0 8px}p{margin:0 0 12px;color:#405961}svg{display:block}svg text{font:16px system-ui;fill:#29454c}</style><main><h1>'+title+'</h1><p>'+subtitle+'</p><svg width="1010" height="423" viewBox="0 0 1010 423">'+body+'</svg></main>'
  const line=(x1,y1,x2,y2,color='#BCCACD')=>'<line x1="'+x1+'" y1="'+y1+'" x2="'+x2+'" y2="'+y2+'" stroke="'+color+'"/>'
  const label=(x,y,text,anchor='start')=>'<text x="'+x+'" y="'+y+'" text-anchor="'+anchor+'">'+xml(text)+'</text>'
  const rect=(x,y,w,h,color='#067467')=>'<rect x="'+x+'" y="'+y+'" width="'+w+'" height="'+h+'" rx="3" fill="'+color+'"/>'
  const left=96, right=970, top=24, base=365, height=base-top
  const startEnergy=Array(24).fill(0)
  for(const row of sessions) startEnergy[Number(row.Hour)]+=Number(row.Energy_kWh)
  const maxEnergy=Math.ceil(Math.max(...startEnergy)/5000)*5000
  const span=(right-left)/24
  const hourly=[0,1,2,3].map(step=>{
    const y=base-step*height/3
    return line(left,y,right,y)+label(left-12,y+5,Math.round(step*maxEnergy/3).toLocaleString(),'end')
  }).join('')+startEnergy.map((energy,h)=>{
    const hgt=energy/maxEnergy*height
    return rect(left+h*span+4,base-hgt,span-8,hgt)+label(left+(h+0.5)*span,base+24,h,'middle')
  }).join('')+label(535,base+50,'Session start hour','middle')
  write(path.join(out,'voltpulse-hourly.html'),chart('Energy delivered by session start hour','Synthetic Indian sessions · Total session energy in kWh, grouped by start hour',hourly))
  const modelRows=scores.slice(0,2)
  const models=[{name:'Gradient boosting',color:'#39759A'},{name:'Random Forest',color:'#067467'}]
  const regLeft=200, regSpan=720
  const reg=[0,2,4,6,8,10].map(x=>{
    const px=regLeft+regSpan*x/10
    return line(px,40,px,300)+label(px,330,x,'middle')
  }).join('')+modelRows.map((row,i)=>{
    const y=85+115*i, w=row.RMSE*regSpan/10
    return label(regLeft-12,y+30,models[i].name,'end')+rect(regLeft,y,w,48,models[i].color)+label(regLeft+w+11,y+30,row.RMSE.toFixed(4))
  }).join('')+label(regLeft+regSpan/2,371,'RMSE (kWh)','middle')
  write(path.join(out,'voltpulse-regression.html'),chart('Session energy prediction error','Saved scikit-learn benchmark · Same holdout split for both regressors',reg))
  const coords=Array.from(new Map(sessions.map(r=>[r.Latitude+','+r.Longitude,[Number(r.Latitude),Number(r.Longitude)]])).values())
  const centroids=scores[4].Recommended_Centroids_Lat_Lon
  const lat=[28.42,28.68], lon=[77.04,77.62]
  const x=value=>left+(value-lon[0])/(lon[1]-lon[0])*(right-left)
  const y=value=>base-(value-lat[0])/(lat[1]-lat[0])*height
  const dot=(px,py,r,fill)=>'<circle cx="'+px+'" cy="'+py+'" r="'+r+'" fill="'+fill+'"/>'
  const loc=[28.45,28.5,28.55,28.6,28.65].map(n=>line(left,y(n),right,y(n))+label(left-11,y(n)+5,n.toFixed(2),'end')).join('')+
    [77.1,77.2,77.3,77.4,77.5,77.6].map(n=>line(x(n),top,x(n),base)+label(x(n),base+24,n.toFixed(2),'middle')).join('')+
    coords.map(([a,b])=>dot(x(b),y(a),6,'#39759A')).join('')+centroids.map(([a,b])=>rect(x(b)-7,y(a)-7,14,14,'#DB6A26')).join('')+
    label(530,base+50,'Longitude (°E)','middle')+label(5,14,'Lat (°N)')+dot(660,15,5,'#39759A')+label(674,20,'Session location')+rect(837,9,12,12,'#DB6A26')+label(859,20,'Centroid')
  write(path.join(out,'voltpulse-clusters.html'),chart('Station coordinates and K-means centroids','Synthetic Indian experiment · Four clusters from the saved scikit-learn benchmark',loc))
  const nodes = [
    ['Generated sessions','ETL and features','Model experiments','BI scorecard'],
    ['Open Charge Map','Station snapshot','Browser map and routing','Driver and planner'],
    ['Simulated events','JSONL fixture','Python replay','Console summary']
  ]
  const flow = nodes.map((row,i)=>row.map((item,j)=>{
    const x=5+j*254, y=34+i*108
    const next=x+234
    return rect(x,y,220,65,'#E5F3F1')+label(x+110,y+39,item,'middle')+
      (j===3?'':line(x+220,y+32,next+14,y+32,'#067467')+
        '<path d="M '+(next+8)+' '+(y+26)+' l 7 6 l -7 6" fill="none" stroke="#067467" stroke-width="2"/>')
  }).join('')).join('')
  write(path.join(out,'voltpulse-flow.html'),chart('VoltPulse data flow','Figure 2.1 · Session experiment, station discovery and simulated telemetry replay',flow))
}
