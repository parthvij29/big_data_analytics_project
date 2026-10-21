"""
generate_milestone1_report.py
-----------------------------
Generates the official Milestone 1 Word Document (.docx) for CSET 371:
Big Data Analytics and Business Intelligence, Bennett University.

Follows the exact format template provided by the university.

Includes:
- Title Page (with Bennett University logo, header logos)
- Declaration & Plagiarism Certification
- Teamwork & Collaboration Table
- Table of Contents
- Chapter 1: Problem Domain Identification and Analysis (1.1 to 1.11)
- Chapter 2: Project Design and Methodology (2.1 to 2.11)

Target: ~20 pages, Milestone 1 only.
"""

import docx
from docx.shared import Inches, Pt, RGBColor, Cm, Emu
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.section import WD_ORIENT
from docx.oxml.ns import qn
import os

REPORT_DIR = os.path.dirname(os.path.abspath(__file__))
DIAGRAM_DIR = os.path.join(REPORT_DIR, "diagrams")
FORMAT_ASSETS = os.path.join(REPORT_DIR, "format_assets", "word", "media")

# Paths for logos extracted from the format template
LOGO_BENNETT = os.path.join(FORMAT_ASSETS, "image1.jpeg")       # large Bennett logo
LOGO_TIMES   = os.path.join(FORMAT_ASSETS, "image2.png")        # Times Group logo for header
LOGO_BU_SMALL = os.path.join(FORMAT_ASSETS, "image3.png")       # small BU logo for header


def create_report(output_path=None):
    if output_path is None:
        output_path = os.path.join(REPORT_DIR, "VoltPulse_Milestone1_Report.docx")

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    doc = docx.Document()

    # ── page setup ──
    for section in doc.sections:
        section.top_margin    = Cm(2.5)
        section.bottom_margin = Cm(1.8)
        section.left_margin   = Cm(2.0)
        section.right_margin  = Cm(2.0)
        section.page_width    = Inches(8.5)
        section.page_height   = Inches(11)

    # ── add header with logos (matching the format template) ──
    header = doc.sections[0].header
    header.is_linked_to_previous = False
    htable = header.add_table(rows=1, cols=2, width=Inches(6.5))
    htable.alignment = WD_TABLE_ALIGNMENT.CENTER

    # Left cell – BU small logo
    left_cell = htable.cell(0, 0)
    left_cell.width = Inches(3.25)
    lp = left_cell.paragraphs[0]
    lp.alignment = WD_ALIGN_PARAGRAPH.LEFT
    if os.path.exists(LOGO_BU_SMALL):
        lp.add_run().add_picture(LOGO_BU_SMALL, width=Inches(1.5))

    # Right cell – Times Group logo
    right_cell = htable.cell(0, 1)
    right_cell.width = Inches(3.25)
    rp = right_cell.paragraphs[0]
    rp.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    if os.path.exists(LOGO_TIMES):
        rp.add_run().add_picture(LOGO_TIMES, width=Inches(1.5))

    # Remove header table borders
    for cell in htable.columns[0].cells + htable.columns[1].cells:
        tc = cell._tc
        tcPr = tc.get_or_add_tcPr()
        borders = docx.oxml.OxmlElement('w:tcBorders')
        for edge in ('top', 'left', 'bottom', 'right', 'insideH', 'insideV'):
            el = docx.oxml.OxmlElement(f'w:{edge}')
            el.set(qn('w:val'), 'none')
            el.set(qn('w:sz'), '0')
            el.set(qn('w:space'), '0')
            el.set(qn('w:color'), 'auto')
            borders.append(el)
        tcPr.append(borders)

    # ── styling helpers ──
    def set_font(run, name="Times New Roman", size_pt=12, bold=False,
                 italic=False, color=RGBColor(0, 0, 0)):
        run.font.name = name
        run.font.size = Pt(size_pt)
        run.bold = bold
        run.italic = italic
        run.font.color.rgb = color

    def add_para(text, align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_after=6,
                 line_spacing=1.15, bold=False, size=12, indent_left=None):
        p = doc.add_paragraph()
        p.alignment = align
        p.paragraph_format.space_after = Pt(space_after)
        p.paragraph_format.line_spacing = line_spacing
        if indent_left:
            p.paragraph_format.left_indent = Cm(indent_left)
        run = p.add_run(text)
        set_font(run, size_pt=size, bold=bold)
        return p

    def add_heading_chapter(text):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        p.paragraph_format.space_before = Pt(18)
        p.paragraph_format.space_after = Pt(10)
        run = p.add_run(text)
        set_font(run, size_pt=16, bold=True, color=RGBColor(0x1a, 0x3c, 0x6e))
        return p

    def add_heading_2(text):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        p.paragraph_format.space_before = Pt(12)
        p.paragraph_format.space_after = Pt(4)
        run = p.add_run(text)
        set_font(run, size_pt=13, bold=True, color=RGBColor(0x2c, 0x5f, 0x8a))
        return p

    def add_heading_3(text):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        p.paragraph_format.space_before = Pt(8)
        p.paragraph_format.space_after = Pt(2)
        run = p.add_run(text)
        set_font(run, size_pt=12, bold=True)
        return p

    def add_figure(image_path, caption, width=Inches(5.5)):
        if os.path.exists(image_path):
            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            run = p.add_run()
            run.add_picture(image_path, width=width)

            cap = doc.add_paragraph()
            cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
            cap.paragraph_format.space_after = Pt(8)
            r = cap.add_run(caption)
            set_font(r, size_pt=10, italic=True, color=RGBColor(0x55, 0x55, 0x55))

    def add_table_grid(headers, rows, col_widths=None):
        table = doc.add_table(rows=1, cols=len(headers))
        table.style = 'Table Grid'
        table.alignment = WD_TABLE_ALIGNMENT.CENTER

        # header row
        hdr = table.rows[0].cells
        for i, h in enumerate(headers):
            hdr[i].text = ""
            p = hdr[i].paragraphs[0]
            run = p.add_run(h)
            set_font(run, size_pt=10, bold=True, color=RGBColor(255, 255, 255))
            # shade header
            shading = docx.oxml.OxmlElement('w:shd')
            shading.set(qn('w:fill'), '2c5f8a')
            shading.set(qn('w:val'), 'clear')
            hdr[i]._tc.get_or_add_tcPr().append(shading)

        for row_data in rows:
            row_cells = table.add_row().cells
            for i, val in enumerate(row_data):
                row_cells[i].text = ""
                p = row_cells[i].paragraphs[0]
                run = p.add_run(str(val))
                set_font(run, size_pt=10)
        return table

    # ================================================================
    #                        TITLE PAGE (Page 1)
    # ================================================================
    # Blank lines at top
    for _ in range(2):
        p = doc.add_paragraph()
        p.paragraph_format.space_after = Pt(0)

    # Bennett University Logo
    if os.path.exists(LOGO_BENNETT):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = p.add_run()
        run.add_picture(LOGO_BENNETT, width=Inches(2.0))

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(6)
    run = p.add_run("Project Report on")
    set_font(run, size_pt=14)

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_after = Pt(6)

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run("\u201CVoltPulse: A Unified Big Data Analytics & Business Intelligence Platform for Smart EV Charging, Grid Resilience, and Urban Infrastructure Planning\u201D")
    set_font(run, size_pt=20, bold=True)

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(10)
    run = p.add_run("Submitted in Big Data Analytics and Business Intelligence Course, CSET 371")
    set_font(run, size_pt=14)

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(8)
    run = p.add_run("Bachelor of Technology")
    set_font(run, size_pt=14, bold=True)

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run("Of")
    set_font(run, size_pt=14)

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run("Bennett University, Greater Noida")
    set_font(run, size_pt=14, bold=True)

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(10)
    run = p.add_run("By")
    set_font(run, size_pt=12)

    # Student details
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run("Parth Vij\t\t\t\tE24CSU1616")
    set_font(run, size_pt=14)

    # Spacer
    for _ in range(3):
        doc.add_paragraph()

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run("BENNETT UNIVERSITY (THE TIMES GROUP), GREATER NOIDA")
    set_font(run, size_pt=12, bold=True)

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(10)
    run = p.add_run("Under the guidance of")
    set_font(run, size_pt=12)

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run("Faculty Name")
    set_font(run, size_pt=12)

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run("Designation")
    set_font(run, size_pt=12)

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(10)
    run = p.add_run("School of Computer Science Engineering and Technology (SCSET)")
    set_font(run, size_pt=12, bold=True)

    doc.add_page_break()

    # ================================================================
    #                     DECLARATION (Page 2)
    # ================================================================
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(20)
    run = p.add_run("DECLARATION")
    set_font(run, size_pt=16, bold=True)

    add_para(
        "We hereby declare that the project report entitled \u201CVoltPulse: A Unified Big Data Analytics "
        "& Business Intelligence Platform for Smart EV Charging, Grid Resilience, and Urban Infrastructure "
        "Planning\u201D, has not been copied or plagiarized from any other source, and all information, data, "
        "and materials used in this report have been properly acknowledged and cited in the text. "
        "The work has not been submitted previously for any other course project.",
        space_after=12
    )

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(16)
    run = p.add_run("PLAGIARISM REPORT CERTIFICATE")
    set_font(run, size_pt=14, bold=True)

    add_para(
        "Further, the plagiarism similarity index of the report from Turnitin is _____ %, "
        "AI plag is _______% which is within the permissible limit of Turnitin and AI must be 0%. "
        "All sources of information used in the report have been properly acknowledged and cited.",
        space_after=14
    )

    add_para("Student Name: Parth Vij\nEnrollment No.: E24CSU1616", space_after=12)
    add_para("Signature of Team members Candidate", space_after=6)

    doc.add_page_break()

    # ================================================================
    #              TEAMWORK & COLLABORATION (Page 3)
    # ================================================================
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(20)
    run = p.add_run("Teamwork and Collaboration")
    set_font(run, size_pt=16, bold=True)

    add_para("")

    team_headers = ["Team member name", "Enrollment No", "Individual Contribution in Project"]
    team_rows = [
        ["Parth Vij", "E24CSU1616",
         "Complete system design, PySpark ETL pipeline, Kafka streaming simulation, "
         "ML model training and evaluation (5 models), Power BI dashboard, report writing"],
    ]
    add_table_grid(team_headers, team_rows)

    doc.add_page_break()

    # ================================================================
    #                   TABLE OF CONTENTS (Page 4)
    # ================================================================
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(16)
    run = p.add_run("TABLE OF CONTENTS")
    set_font(run, size_pt=16, bold=True)

    add_para("")

    toc_ch1 = (
        "Chapter 1: Problem Domain Identification and Analysis"
    )
    p = doc.add_paragraph()
    run = p.add_run(toc_ch1)
    set_font(run, size_pt=12, bold=True)

    toc_items_1 = [
        "1.1 Background of the Study",
        "1.2 Introduction to the Problem Domain",
        "1.3 Literature Review",
        "1.4 Research Gap and Literature Gaps",
        "1.5 Review of Existing Solutions",
        "1.6 Limitations of Existing Systems",
        "1.7 Problem Statement",
        "1.8 Proposed Solution Overview",
        "1.9 Objectives of the Project",
        "1.10 Scope of the Project",
        "1.11 Industrial Applications and Use Cases",
    ]
    for item in toc_items_1:
        add_para(item, align=WD_ALIGN_PARAGRAPH.LEFT, space_after=2,
                 line_spacing=1.3, indent_left=1.0)

    add_para("")

    toc_ch2 = "Chapter 2: Project Design and Methodology"
    p = doc.add_paragraph()
    run = p.add_run(toc_ch2)
    set_font(run, size_pt=12, bold=True)

    toc_items_2 = [
        "2.1 System Overview",
        "2.2 Proposed System Architecture",
        "2.3 Architecture Components and Their Functions",
        "2.4 Proposed Methodology",
        "2.5 Methodology Workflow Use-case / DFD Flow Diagram",
        "2.6 Algorithms and Techniques Used",
        "2.7 Dataset Description",
        "2.8 Data Collection and Data Preprocessing",
        "2.9 Tools and Technologies Used",
        "2.10 Experimental Setup and Configuration",
        "2.11 Evaluation Metrics",
    ]
    for item in toc_items_2:
        add_para(item, align=WD_ALIGN_PARAGRAPH.LEFT, space_after=2,
                 line_spacing=1.3, indent_left=1.0)

    doc.add_page_break()

    # ================================================================
    #  CHAPTER 1: PROBLEM DOMAIN IDENTIFICATION AND ANALYSIS
    # ================================================================
    add_heading_chapter("CHAPTER 1: PROBLEM DOMAIN IDENTIFICATION AND ANALYSIS")

    # ── 1.1 ──
    add_heading_2("1.1 Background of the Study")
    add_para(
        "The global automotive landscape is in the midst of a once-in-a-century structural "
        "transformation.  Governments on every continent have ratified stringent tailpipe emission "
        "norms, driving automakers to phase out internal combustion engine (ICE) drivetrains in favour "
        "of battery electric vehicles (EVs).  The International Energy Agency estimated that the global "
        "EV fleet surpassed forty million units by the close of 2023, with annual sales growing at "
        "roughly 35 per cent year-on-year.  Projections published by BloombergNEF indicate that electric "
        "vehicles could constitute more than half of all new passenger car sales globally before the end "
        "of this decade."
    )
    add_para(
        "India, too, has accelerated its electric mobility agenda through the FAME-II subsidy scheme and "
        "subsequent PM E-DRIVE programme, targeting cumulative EV registrations in the tens of millions by "
        "2030.  State governments in Delhi, Maharashtra, Karnataka, and Andhra Pradesh have released "
        "dedicated EV policy frameworks offering purchase incentives, reduced registration fees, and "
        "commitments to install public charging corridors along national highway arteries."
    )
    add_para(
        "While the pace of vehicle adoption is encouraging, the supporting charging infrastructure has "
        "lagged considerably.  The mismatch between the rate at which electric cars arrive on city roads "
        "and the rate at which public chargers are deployed creates a compounding bottleneck that affects "
        "three distinct stakeholder groups.  First, electricity distribution utilities see sudden load "
        "surges as hundreds of vehicles plug in during evening commuter hours, threatening transformer "
        "thermal limits and triggering localised voltage sags.  Second, EV owners encounter frustration "
        "when they arrive at a charging station only to find every bay occupied and no indication of the "
        "expected waiting time.  Third, municipal planners and private Charge Point Operators (CPOs) "
        "struggle to identify exactly where the next charging hub should be built to maximise utilisation "
        "and minimise stranded capital."
    )
    add_para(
        "These intertwined challenges demand a data-driven resolution that goes beyond traditional "
        "spreadsheets and periodic status reports.  The sheer volume of telemetry generated by a mid-sized "
        "urban charging network\u2014hundreds of thousands of events each day encompassing plug-in timestamps, "
        "power draws, battery state-of-charge readings, and geospatial coordinates\u2014mandates a distributed "
        "computing framework capable of ingesting, processing, and modelling these streams in near real time."
    )

    # ── 1.2 ──
    add_heading_2("1.2 Introduction to the Problem Domain")
    add_para(
        "The problem domain sits at the crossroads of distributed big data engineering, applied machine "
        "learning, and energy systems analytics.  An electric vehicle is not merely a transportation device; "
        "from the standpoint of the electrical grid it is a high-capacity, mobile load whose power demand "
        "ranges from 7.2 kW for a residential Level 2 wall-box up to 350 kW for a commercial ultra-fast "
        "DC column.  When dozens or hundreds of such loads attach themselves simultaneously to a single "
        "distribution feeder, they can push the local transformer past its rated capacity within minutes."
    )
    add_para(
        "Conventional supervisory control and data acquisition (SCADA) systems deployed by power utilities "
        "aggregate load at the substation level with sampling intervals of fifteen minutes or more.  They "
        "provide no granular visibility into individual charging port states and cannot anticipate a sudden "
        "wave of plug-in events.  On the consumer-facing side, popular navigation and charging-directory "
        "applications such as ChargePoint and PlugShare offer static availability flags that frequently "
        "become stale before the driver physically reaches the station."
    )
    add_para(
        "Legacy relational database management systems struggle when the data velocity, variety, and volume "
        "escalate beyond what a single-node server can accommodate.  A city-wide network of five hundred "
        "charging stations, each equipped with multiple ports, can easily generate several gigabytes of raw "
        "telemetry per day once heartbeat messages, power metering samples, and session metadata are "
        "combined.  Processing this corpus to extract actionable forecasts requires a distributed compute "
        "engine such as Apache Spark, which partitions the workload across multiple CPU cores and memory "
        "pools."
    )

    # ── 1.3 ──
    add_heading_2("1.3 Literature Review")
    add_para(
        "Existing academic research and industrial deployments have investigated isolated aspects of the "
        "electric vehicle charging ecosystem.  A structured survey of the relevant literature reveals "
        "several noteworthy contributions, alongside critical shortcomings that motivate the present work."
    )

    # Literature table
    lit_headers = ["Author / System", "Domain Focus", "Core Methodology", "Key Limitations"]
    lit_rows = [
        ["Caltech ACN-Data\n(Lee et al., 2020)",
         "Campus Charging\nSession Analytics",
         "Centralised logging of 30 000+\nsessions; dwell-time analysis",
         "Research sandbox only;\nno streaming or BI dashboards"],
        ["Zhang et al.\n(IEEE Trans. Smart\nGrid, 2022)",
         "Substation Load\nBalancing",
         "Mixed-Integer Linear\nProgramming optimisation",
         "Does not scale to city-level;\nignores driver behaviour"],
        ["Palo Alto Smart\nCity Initiative\n(2021)",
         "Municipal EV\nMonitoring",
         "Static SQL reports\nand batch tabular views",
         "No real-time streaming;\nno predictive ML models"],
        ["ChargePoint /\nPlugShare\n(Commercial)",
         "Consumer Charging\nDirectory",
         "Crowd-sourced check-ins\nand station status flags",
         "Proprietary; no grid-side\nvisibility or planning tools"],
        ["Sortomme & El-Sharkawi\n(IEEE Trans. Power\nSystems, 2011)",
         "Optimal EV Charging\nScheduling",
         "Quadratic programming\nfor valley-filling",
         "Single-objective; ignores\nstochastic driver arrivals"],
    ]
    add_table_grid(lit_headers, lit_rows)
    add_para("")

    add_para(
        "The Caltech Adaptive Charging Network (ACN-Data) project established one of the earliest "
        "publicly accessible repositories of real-world EV charging session records.  Researchers "
        "analysed connection and active charging durations across workplace and residential contexts, "
        "revealing that vehicles frequently remain plugged in far beyond the period of active energy "
        "transfer.  However, the ACN-Data infrastructure remained confined to a research campus setting "
        "without integration into distribution utility SCADA systems or municipal planning dashboards."
    )
    add_para(
        "Zhang et al. formulated the transformer overload avoidance problem as a mixed-integer linear "
        "programme (MILP) that schedules charging sessions to flatten peak demand.  Although the "
        "mathematical formulation is rigorous, its computational complexity renders it impractical for "
        "real-time operations across hundreds of stations.  Furthermore, the model treats driver arrival "
        "patterns as deterministic, neglecting the stochastic queuing dynamics that govern actual charging "
        "hub utilisation."
    )
    add_para(
        "Municipal open data portals in cities such as Boulder (Colorado) and Palo Alto (California) "
        "publish historical session logs containing timestamps, energy readings, geospatial coordinates, "
        "and charger types.  These datasets are invaluable for retrospective analysis but are not "
        "accompanied by streaming pipelines, machine learning models, or multi-persona decision dashboards."
    )

    # ── 1.4 ──
    add_heading_2("1.4 Research Gap and Literature Gaps")
    add_para(
        "A critical synthesis of the foregoing literature reveals three primary research gaps that "
        "the VoltPulse platform is designed to address:"
    )
    add_para(
        "First, existing systems adopt a siloed architectural philosophy.  Grid-facing tools optimise "
        "transformer utilisation without considering commuter convenience, while consumer-facing "
        "applications display static availability maps without feeding any data back into utility "
        "planning loops.  There is no integrated platform that serves the utility operator, the EV "
        "driver, and the urban planner from a single data backbone.",
        indent_left=0.5
    )
    add_para(
        "Second, the majority of published approaches rely on offline, batch-trained models.  They "
        "download historical session logs, run a training script, and report accuracy metrics in a "
        "research paper.  Critically, none of these works demonstrate a live streaming pipeline that "
        "ingests telemetry events as they occur, computes windowed aggregations in near real time, and "
        "triggers automated alerts when the grid is approaching overload.",
        indent_left=0.5
    )
    add_para(
        "Third, there is a conspicuous disconnect between the machine learning intelligence layer and "
        "the business intelligence presentation layer.  Predictive models trained in Jupyter notebooks "
        "rarely reach the hands of executive decision-makers in a form they can interact with.  This "
        "gap means that valuable forecasts about demand surges, congestion patterns, and optimal hub "
        "locations remain buried in CSV files rather than powering interactive Power BI or Streamlit "
        "dashboards.",
        indent_left=0.5
    )

    # ── 1.5 ──
    add_heading_2("1.5 Review of Existing Solutions")
    add_para(
        "Commercial charging management systems (CMS) currently deployed by network operators such as "
        "ChargePoint, Shell Recharge, and Electrify America use proprietary cloud back-ends with closed "
        "communication protocols.  These systems are primarily designed for session billing, remote "
        "diagnostics, and basic uptime reporting.  They do not expose raw telemetry to distribution "
        "utilities, nor do they incorporate spatial clustering algorithms for siting new infrastructure."
    )
    add_para(
        "On the utility side, power grid operators depend on legacy SCADA and distribution management "
        "systems (DMS) that sample aggregate feeder loads at fifteen-minute intervals.  These systems "
        "are well suited for monitoring conventional residential and commercial loads but are architecturally "
        "ill-equipped to handle the rapid, high-magnitude transients introduced by DC fast chargers.  "
        "A single 350 kW fast charger can add the equivalent load of thirty average households to a feeder "
        "within seconds of a vehicle plugging in."
    )
    add_para(
        "Navigation and trip-planning applications such as Google Maps, Waze, and A Better Route Planner "
        "incorporate charging station directories, but their availability indicators are typically based "
        "on periodic polling rather than real-time telemetry streams.  The information a driver sees on "
        "screen may be minutes or even hours behind the actual station state, leading to wasted detours "
        "and increased anxiety."
    )

    # ── 1.6 ──
    add_heading_2("1.6 Limitations of Existing Systems")
    add_para("The foregoing review exposes four systemic limitations:")
    add_para(
        "1.  Scalability Ceiling:  Single-node databases and centralised batch processors cannot keep "
        "pace with the velocity and volume of telemetry generated by a metropolitan charging network.  "
        "As the fleet grows, query latencies escalate and batch windows widen, rendering analytics stale "
        "before they reach the operator.\n\n"
        "2.  Absence of Multi-Horizon Forecasting:  Current deployments lack machine learning models "
        "that predict demand surges one hour, four hours, or twenty-four hours in advance.  Without "
        "such forecasts, utilities cannot proactively curtail non-essential loads or pre-position mobile "
        "energy storage.\n\n"
        "3.  Heuristic Siting Decisions:  New chargers are often placed according to political boundaries, "
        "land availability, or developer convenience rather than empirical charging demand patterns.  "
        "The result is a patchwork of over-served corridors and under-served \u201Ccharging deserts\u201D where "
        "drivers have no public charging option within a five-kilometre radius.\n\n"
        "4.  No Unified Stakeholder Interface:  Grid operators, drivers, and planners each use separate, "
        "incompatible tools.  Data flows in one direction\u2014from the charger to a billing back-end\u2014without "
        "lateral sharing across stakeholder roles."
    )

    # ── 1.7 ──
    add_heading_2("1.7 Problem Statement")
    add_para(
        "The central problem addressed by this project is as follows: to design and implement a "
        "distributed big data analytics platform (VoltPulse) that leverages Apache Spark, Spark "
        "Structured Streaming, and PySpark MLlib to accomplish the following objectives simultaneously:"
    )
    add_para(
        "\u2022  Ingest and process high-volume EV charging session logs and simulated real-time telemetry "
        "streams using a scalable distributed ETL pipeline.\n"
        "\u2022  Execute windowed aggregations on live power draw data and trigger automated alerts when "
        "instantaneous grid load exceeds 85 per cent of the rated transformer capacity.\n"
        "\u2022  Train and benchmark five machine learning models\u2014encompassing regression, classification, "
        "and unsupervised clustering\u2014to forecast energy demand, classify station congestion, predict "
        "session duration, and recommend optimal hub locations.\n"
        "\u2022  Surface the resulting intelligence through a multi-persona business intelligence dashboard "
        "serving grid administrators, EV drivers, and urban infrastructure planners."
    )

    # ── 1.8 ──
    add_heading_2("1.8 Proposed Solution Overview")
    add_para(
        "VoltPulse is conceived as an end-to-end enterprise EV charging intelligence system organised "
        "around three role-specific analytical portals, all drawing from a single distributed data "
        "lakehouse:"
    )
    add_para(
        "Admin / Power Grid Operations Console \u2014  This portal provides real-time visibility into "
        "aggregate power draw across all monitored charging stations.  A predictive twenty-four-hour "
        "load curve, produced by a Gradient Boosted Tree (GBT) regressor, is overlaid on the actual "
        "consumption trace, enabling grid operators to anticipate transformer stress windows and dispatch "
        "demand-response signals proactively.",
        indent_left=0.5, bold=True, size=11
    )
    add_para(
        "EV Driver Companion Portal \u2014  Drivers access a lightweight interface that displays live bay "
        "occupancy at nearby stations, a colour-coded congestion gauge (Low / Moderate / High) produced "
        "by a Random Forest classifier, and an estimated remaining charging time derived from a Linear "
        "Regression model.  These indicators reduce range anxiety and eliminate unnecessary detours.",
        indent_left=0.5, bold=True, size=11
    )
    add_para(
        "Urban Infrastructure Planning Portal \u2014  City planners interact with a geospatial bubble map "
        "highlighting high-density charging demand zones, K-Means cluster centroids recommending optimal "
        "coordinates for future hubs, and an overlay identifying urban corridors classified as charging "
        "deserts.",
        indent_left=0.5, bold=True, size=11
    )

    add_figure(os.path.join(DIAGRAM_DIR, "system_architecture.png"),
               "Figure 1.1: VoltPulse Four-Layer System Architecture Overview")

    # ── 1.9 ──
    add_heading_2("1.9 Objectives of the Project")
    add_para(
        "The objectives of this project are enumerated below with explicit alignment to the "
        "technological stack and university rubric requirements:"
    )
    add_para(
        "Objective 1 \u2013 Distributed Data Lakehouse Construction:  Design and deploy a PySpark-based "
        "ETL pipeline that ingests the City of Boulder electric vehicle charging session dataset "
        "(5 000 records, 17 attributes), performs temporal decomposition, outlier filtering, and "
        "categorical encoding, and persists the cleaned corpus in both CSV and Apache Parquet columnar "
        "formats for high-performance analytical queries."
    )
    add_para(
        "Objective 2 \u2013 Real-Time Streaming Telemetry:  Architect a simulated Apache Kafka event "
        "producer that emits JSON telemetry packets (plug-in events, power metering heartbeats, and "
        "plug-out notifications) and a Spark Structured Streaming consumer that computes rolling "
        "fifteen-minute and one-hour windowed power load aggregations."
    )
    add_para(
        "Objective 3 \u2013 Predictive Grid Load Forecasting:  Train and cross-validate two distributed "
        "regression models (GBTRegressor and RandomForestRegressor) using PySpark MLlib to forecast "
        "next-hour aggregate energy consumption (kWh) and evaluate their predictive accuracy using "
        "RMSE, MAE, and R-squared."
    )
    add_para(
        "Objective 4 \u2013 Congestion Classification and Duration Modelling:  Formulate a multi-class "
        "Random Forest classifier to predict bay congestion levels (Low, Moderate, High) and a Linear "
        "Regression model to estimate individual session charging duration, providing actionable "
        "intelligence to EV drivers."
    )
    add_para(
        "Objective 5 \u2013 Spatial Siting Optimisation:  Implement distributed K-Means clustering on "
        "geospatial coordinate pairs (Latitude, Longitude) weighted by historical energy consumption "
        "to identify optimal centroid locations for future charging hub deployment."
    )
    add_para(
        "Objective 6 \u2013 Multi-Persona Business Intelligence Dashboard:  Construct an interactive, "
        "role-based dashboard (Power BI / Streamlit) that provides tailored visual analytics for grid "
        "operators, EV drivers, and urban planners through dedicated tabs with contextual filters and "
        "drill-down capabilities."
    )

    # ── 1.10 ──
    add_heading_2("1.10 Scope of the Project")
    add_para(
        "The scope of VoltPulse encompasses the full lifecycle of a big data analytics project, from "
        "data acquisition through model evaluation to dashboard delivery.  Specifically, the platform "
        "addresses:"
    )
    add_para(
        "\u2022  Ingestion and modelling of municipal Level 2 and DC Fast Charging session logs from the "
        "City of Boulder Open Data repository (5 000 records across 10 distinct station facilities).\n"
        "\u2022  Simulated real-time streaming using Apache Kafka and Spark Structured Streaming to mimic "
        "a live metropolitan telemetry pipeline.\n"
        "\u2022  Training and evaluation of five machine learning models covering regression (energy demand, "
        "session duration), classification (congestion tiers), and unsupervised clustering (spatial hub "
        "siting).\n"
        "\u2022  Construction of an interactive, multi-tab business intelligence dashboard using Power BI "
        "Desktop and a complementary Streamlit web prototype.\n"
        "\u2022  Alignment with United Nations Sustainable Development Goals 7, 11, and 13."
    )
    add_para(
        "Items explicitly outside the project scope include physical electrical circuit redesign, "
        "procurement of commercial charging hardware, negotiation with utility rate structures, and "
        "deployment to a production Kubernetes cluster.  The platform operates on a local Spark cluster "
        "(local[*] mode) and serves as a proof-of-concept demonstrating how distributed analytics can "
        "guide real-world EV infrastructure decisions."
    )

    # ── 1.11 ──
    add_heading_2("1.11 Industrial Applications and Use Cases")
    add_para(
        "The techniques and architecture demonstrated by VoltPulse have direct applicability across "
        "multiple industry verticals:"
    )
    add_para(
        "Smart Electric Utilities (Network Operations Centres):  Distribution utilities can deploy the "
        "streaming telemetry and GBT forecasting modules to implement automated demand-response "
        "dispatching.  When predicted load exceeds transformer headroom, the system triggers curtailment "
        "signals to deferrable charging sessions, shaving peak demand and avoiding costly infrastructure "
        "upgrades.",
        indent_left=0.5
    )
    add_para(
        "Charge Point Operators (CPOs):  Private charging network operators such as Tata Power EZ Charge "
        "or Ather Grid can utilise the congestion classification and duration prediction models to "
        "implement dynamic pricing.  During periods of high demand, a modest price premium incentivises "
        "drivers to shift sessions to off-peak hours, improving station throughput.",
        indent_left=0.5
    )
    add_para(
        "Municipal Urban Planning Departments:  The spatial clustering module identifies under-served "
        "geographic corridors where a new charging hub would attract the highest utilisation.  Capital "
        "investment committees can overlay cluster centroids on municipal zoning maps to prioritise "
        "construction permits and land acquisition.",
        indent_left=0.5
    )
    add_para(
        "Commercial Fleet Operators:  Last-mile delivery companies and electric bus transit agencies can "
        "integrate the load forecasting API to schedule depot charging during overnight valley-fill "
        "windows, reducing per-kWh energy costs and avoiding penalties for exceeding contracted demand.",
        indent_left=0.5
    )

    doc.add_page_break()

    # ================================================================
    #  CHAPTER 2: PROJECT DESIGN AND METHODOLOGY
    # ================================================================
    add_heading_chapter("CHAPTER 2: PROJECT DESIGN AND METHODOLOGY")

    # ── 2.1 ──
    add_heading_2("2.1 System Overview")
    add_para(
        "VoltPulse is engineered as a decoupled, four-tier distributed big data platform.  Each tier "
        "operates independently behind well-defined data interfaces, enabling individual components to "
        "be upgraded, scaled, or replaced without disrupting the rest of the pipeline.  The four tiers "
        "are: (i) Data Ingestion and Streaming, (ii) Distributed Spark Processing and Lakehouse Storage, "
        "(iii) PySpark MLlib Machine Learning Intelligence Engine, and (iv) Role-Based Business "
        "Intelligence and Decision Support."
    )
    add_para(
        "The ingestion tier accepts data from two sources.  The primary source is a batch CSV file "
        "containing 5 000 authenticated historical charging sessions published by the City of Boulder, "
        "Colorado.  The secondary source is a simulated Apache Kafka event stream that emits JSON "
        "telemetry packets at configurable intervals, mimicking real-time plug-in events, power "
        "metering heartbeats, and plug-out notifications."
    )
    add_para(
        "The processing tier uses PySpark to distribute cleaning, transformation, and feature engineering "
        "tasks across multiple CPU cores.  Cleaned records are persisted in both CSV and Apache Parquet "
        "formats, the latter being a columnar storage layout that supports predicate pushdown and "
        "partition pruning for efficient analytical queries."
    )
    add_para(
        "The intelligence tier houses five machine learning models trained using PySpark MLlib and "
        "scikit-learn.  These models address three distinct use cases: hourly energy demand forecasting, "
        "station congestion classification with session duration prediction, and spatial hub siting "
        "optimisation."
    )
    add_para(
        "The presentation tier delivers insights through a Power BI Desktop dashboard with three "
        "role-specific tabs and a complementary Streamlit web application for real-time interaction."
    )

    # ── 2.2 ──
    add_heading_2("2.2 Proposed System Architecture")
    add_para(
        "The architectural blueprint follows a modern data lakehouse design pattern.  Raw data lands "
        "in an ingestion staging area, passes through a distributed transformation engine, settles into "
        "columnar storage, flows through the machine learning suite, and finally reaches the visualisation "
        "layer.  The diagram below illustrates the end-to-end data journey across all four tiers."
    )

    add_figure(os.path.join(DIAGRAM_DIR, "system_architecture.png"),
               "Figure 2.1: VoltPulse Four-Layer System Architecture")

    add_para(
        "The architecture deliberately separates compute from storage.  The Spark processing engine "
        "reads from and writes to Parquet files on local disk (or HDFS in a production deployment), "
        "ensuring that scaling the compute cluster does not require restructuring the storage layer.  "
        "Similarly, the BI dashboard connects to the processed output tables through standard file "
        "connectors, making it agnostic to whether the upstream processing was performed by Spark, "
        "Pandas, or a cloud-managed service."
    )

    # ── 2.3 ──
    add_heading_2("2.3 Architecture Components and Their Functions")
    add_para(
        "Each component within the four-tier architecture serves a specific operational function:"
    )

    comp_headers = ["Component", "Tier", "Function"]
    comp_rows = [
        ["Kafka Event Producer", "Ingestion",
         "Emits high-frequency JSON telemetry packets mimicking real-time vehicle plug-in events and power meter readings"],
        ["Spark Structured Streaming\nConsumer", "Ingestion /\nProcessing",
         "Subscribes to the Kafka topic and maintains stateful watermarked aggregations using tumbling 15-minute windows"],
        ["PySpark Batch ETL Engine", "Processing",
         "Reads historical CSV logs, performs timestamp parsing, null handling, feature engineering, and writes cleaned Parquet"],
        ["VectorAssembler &\nStandardScaler", "Processing",
         "Assembles numeric feature columns into dense vectors and normalises them for model training"],
        ["MLlib Model Executors", "Intelligence",
         "Trains five distributed models (GBT, RF Regressor, RF Classifier, Linear Regression, K-Means) with cross-validation"],
        ["Power BI / Streamlit UI", "Presentation",
         "Renders three role-specific tabs with interactive filters, drill-down charts, and geospatial bubble maps"],
    ]
    add_table_grid(comp_headers, comp_rows)

    add_figure(os.path.join(DIAGRAM_DIR, "streaming_pipeline.png"),
               "Figure 2.2: Real-Time Streaming Telemetry Pipeline")

    # ── 2.4 ──
    add_heading_2("2.4 Proposed Methodology")
    add_para(
        "The project methodology adapts the Cross-Industry Standard Process for Data Mining (CRISP-DM) "
        "framework to the distributed big data context.  CRISP-DM organises analytical projects into "
        "six iterative phases: business understanding, data understanding, data preparation, modelling, "
        "evaluation, and deployment.  VoltPulse maps each phase to a concrete deliverable within the "
        "university milestone schedule:"
    )
    add_para(
        "Phase 1 \u2013 Domain Modelling and Dataset Acquisition:  Identify the three stakeholder personas "
        "(grid operator, EV driver, urban planner) and acquire the City of Boulder Open Data charging "
        "session corpus."
    )
    add_para(
        "Phase 2 \u2013 PySpark Schema Definition, Cleaning, and Null Imputation:  Define the target schema, "
        "parse date-time strings into native timestamp columns, handle missing values through median "
        "imputation or row exclusion, and filter anomalous records."
    )
    add_para(
        "Phase 3 \u2013 Temporal Feature Decomposition and Spatial Encoding:  Extract hour-of-day, "
        "day-of-week, weekend indicator, charger type flag, and derive the congestion target variable."
    )
    add_para(
        "Phase 4 \u2013 MLlib Model Formulation, Hyperparameter Grid Search, and Distributed Cross-Validation:  "
        "Train each model using an 80/20 train-test split, perform grid search over key hyperparameters, "
        "and record evaluation metrics."
    )
    add_para(
        "Phase 5 \u2013 Power BI Dashboard Construction and DAX Measure Definition:  Design the three-tab "
        "layout, connect to processed data sources, define calculated measures, and build interactive "
        "visualisations."
    )
    add_para(
        "Phase 6 \u2013 Comprehensive Model Benchmarking and University Deliverable Compilation:  Compare "
        "model accuracy across algorithms, compile the project report, and prepare the viva voce "
        "demonstration."
    )

    add_figure(os.path.join(DIAGRAM_DIR, "crisp_dm_workflow.png"),
               "Figure 2.3: Adapted CRISP-DM Methodology Lifecycle")

    # ── 2.5 ──
    add_heading_2("2.5 Methodology Workflow Use-case / DFD Flow Diagram")
    add_para(
        "The Data Flow Diagram (DFD) at Level 1 traces the journey of a single data record from its "
        "point of origin through every transformation stage to its final presentation on the dashboard.  "
        "Raw session logs and live Kafka events enter the PySpark ETL cleaning stage, where timestamp "
        "parsing, null removal, and feature derivation occur.  The cleaned records are then assembled "
        "into feature vectors using VectorAssembler.  These vectors feed the five MLlib models, whose "
        "outputs are persisted as Parquet tables in the lakehouse.  The dashboard layer reads these "
        "tables and renders interactive visualisations for each stakeholder persona."
    )

    add_figure(os.path.join(DIAGRAM_DIR, "dfd_level1.png"),
               "Figure 2.4: Data Flow Diagram \u2014 DFD Level 1")

    add_figure(os.path.join(DIAGRAM_DIR, "etl_flowchart.png"),
               "Figure 2.5: ETL Pipeline Step-by-Step Processing Flowchart")

    # ── 2.6 ──
    add_heading_2("2.6 Algorithms and Techniques Used")
    add_para(
        "The VoltPulse intelligence engine incorporates five machine learning algorithms, each selected "
        "for a specific analytical use case.  The rationale for each choice and its mathematical "
        "formulation are detailed below."
    )

    add_heading_3("2.6.1 Gradient Boosted Tree Regressor (GBTRegressor)")
    add_para(
        "For hourly grid load forecasting, gradient boosted trees construct a sequence of shallow "
        "decision trees, each fitted to the pseudo-residuals of the preceding ensemble.  At iteration m, "
        "given the current ensemble prediction F_{m-1}(x), the algorithm computes the negative gradient "
        "of the loss function with respect to the prediction and fits a new base learner h_m(x) to these "
        "pseudo-residuals.  The ensemble is then updated as F_m(x) = F_{m-1}(x) + gamma_m * h_m(x), "
        "where gamma_m is the step-size (learning rate).  GBT captures non-linear diurnal patterns, "
        "weather-induced fluctuations, and commuter arrival spikes with superior fidelity compared to "
        "simple linear regression."
    )
    add_para(
        "Hyperparameters:  n_estimators = 100, max_depth = 5, learning_rate = 0.1."
    )

    add_heading_3("2.6.2 Random Forest Regressor (RandomForestRegressor)")
    add_para(
        "As a benchmark comparison for the GBT model, a Random Forest regressor constructs an ensemble "
        "of B bootstrap-aggregated decision trees.  Each tree is trained on a random subset of the "
        "training data with random feature sub-selection at every split node.  The final prediction is "
        "the arithmetic mean of all individual tree predictions.  Random forests are inherently resistant "
        "to overfitting and provide robust baseline performance."
    )
    add_para(
        "Hyperparameters:  n_estimators = 100, max_depth = 8."
    )

    add_heading_3("2.6.3 Random Forest Classifier (RandomForestClassifier)")
    add_para(
        "Station bay congestion is classified into three discrete tiers: Low (0), Moderate (1), and "
        "High (2).  The classifier builds B independent decision trees using bootstrapped training "
        "samples.  For a new observation x, each tree casts a vote for one of the three classes, and "
        "the final prediction is determined by majority voting.  The model is evaluated using multi-class "
        "accuracy, weighted precision, weighted recall, and weighted F1-score."
    )
    add_para(
        "Hyperparameters:  n_estimators = 100, max_depth = 6."
    )

    add_heading_3("2.6.4 Linear Regression (LinearRegression)")
    add_para(
        "Individual session charging duration is predicted using ordinary least squares linear "
        "regression.  The model assumes a linear relationship between the feature vector "
        "x = [Energy_kWh, IsDCFC, Hour, IsWeekend] and the response variable y (charging duration in "
        "minutes).  The parameter vector beta is estimated by minimising the sum of squared residuals.  "
        "Linear regression offers high interpretability and fast inference, making it suitable for "
        "real-time duration estimates displayed to drivers upon plug-in."
    )

    add_heading_3("2.6.5 K-Means Spatial Clustering (KMeans)")
    add_para(
        "To recommend candidate coordinates for future charging hubs, K-Means partitions N historical "
        "high-energy-usage coordinate pairs (Latitude, Longitude) into K disjoint clusters by minimising "
        "the within-cluster sum of squares (WCSS / Inertia).  The algorithm alternates between assigning "
        "each point to its nearest centroid and recomputing centroids as the geometric mean of their "
        "assigned points, iterating until convergence.  The optimal number of clusters is validated using "
        "the Silhouette Score, which measures how similar each point is to its own cluster compared to "
        "neighbouring clusters."
    )
    add_para(
        "Configuration:  K = 4 clusters, n_init = 10 random restarts."
    )

    # ── 2.7 ──
    add_heading_2("2.7 Dataset Description")
    add_para(
        "The primary dataset used in this project is sourced from the City of Boulder Open Data portal "
        "and represents authentic electric vehicle charging station energy consumption records.  The "
        "dataset contains 5 000 charging sessions recorded across 10 municipal charging stations in "
        "Boulder, Colorado.  Each record captures the complete lifecycle of a single charging event, "
        "from the moment a vehicle plugs in to the moment it disconnects."
    )
    add_para(
        "The dataset comprises 17 raw attributes, including the station name, street address, "
        "geospatial coordinates (latitude and longitude), session start and end timestamps, total "
        "connection duration, active charging duration, energy transferred in kilowatt-hours, charger "
        "port type (Level 2 AC or DC Fast), port number, and an anonymised user identifier."
    )

    add_figure(os.path.join(DIAGRAM_DIR, "dataset_schema.png"),
               "Figure 2.6: City of Boulder EV Charging \u2014 Dataset Schema")

    add_para(
        "In addition to the raw attributes, the ETL pipeline derives several engineered features that "
        "serve as inputs to the machine learning models: Hour (extracted from the session start timestamp), "
        "DayOfWeek (1 = Sunday through 7 = Saturday), IsWeekend (binary flag), IsDCFC (binary flag "
        "indicating DC Fast Charger), Energy_kWh (cast to double precision), Duration_Mins (total "
        "connection time), Charging_Mins (active energy transfer time), and Congestion_Level "
        "(categorical target: 0 = Low, 1 = Moderate, 2 = High, derived from time-of-day heuristics)."
    )

    # ── 2.8 ──
    add_heading_2("2.8 Data Collection and Data Preprocessing")
    add_para(
        "Data collection follows a two-track approach.  The first track downloads the City of Boulder "
        "Open Data CSV file, which serves as the authoritative historical record for batch model training "
        "and evaluation.  The second track generates simulated real-time telemetry using a custom Python "
        "Kafka producer that emits JSON-Lines events to a local buffer file."
    )
    add_para(
        "The preprocessing pipeline, implemented in PySpark, performs the following transformations:"
    )
    add_para(
        "1.  Timestamp Parsing:  The raw Start_Date_Time and End_Date_Time string columns are cast to "
        "native Spark TimestampType columns using to_timestamp().\n\n"
        "2.  Temporal Feature Extraction:  The hour of day, day of week, and weekend indicator are "
        "derived from the parsed timestamps using PySpark SQL functions (hour(), dayofweek()).\n\n"
        "3.  Charger Type Encoding:  The Port_Type categorical column is converted to a binary integer "
        "flag (IsDCFC = 1 for DC Fast, 0 for Level 2).\n\n"
        "4.  Congestion Target Derivation:  Peak commuter hours (07:00\u201308:00, 12:00, 17:00\u201319:00) are "
        "labelled as High congestion (2), midday working hours as Moderate (1), and all other hours as "
        "Low (0).\n\n"
        "5.  Numeric Casting:  Energy and duration columns are explicitly cast to DoubleType to ensure "
        "compatibility with MLlib vector assembly.\n\n"
        "6.  Null and Outlier Handling:  Records with null energy readings or charging durations "
        "exceeding twelve hours are flagged for review or excluded from the training set."
    )

    add_figure(os.path.join(DIAGRAM_DIR, "etl_flowchart.png"),
               "Figure 2.7: ETL Pipeline Processing Flowchart")

    # ── 2.9 ──
    add_heading_2("2.9 Tools and Technologies Used")

    add_figure(os.path.join(DIAGRAM_DIR, "tech_stack.png"),
               "Figure 2.8: VoltPulse Technology Stack Overview")

    tech_headers = ["Category", "Tool / Library", "Role in VoltPulse"]
    tech_rows = [
        ["Distributed Compute", "Apache Spark 3.5 / PySpark",
         "Distributed ETL, feature engineering, and model training"],
        ["Stream Processing", "Apache Kafka & Spark\nStructured Streaming",
         "Real-time telemetry ingestion and windowed aggregations"],
        ["Machine Learning", "PySpark MLlib / Scikit-learn",
         "Training GBT, RF, Linear Regression, and K-Means models"],
        ["Business Intelligence", "Microsoft Power BI Desktop",
         "Three-tab interactive dashboard with DAX measures"],
        ["Web Prototype", "Streamlit & Plotly",
         "Real-time web application for streaming visualisation"],
        ["Storage Format", "Apache Parquet / CSV",
         "Columnar lakehouse storage with partition pruning"],
        ["Language", "Python 3.14",
         "End-to-end scripting, orchestration, and model evaluation"],
        ["Version Control", "Git & GitHub",
         "Source code management and collaborative development"],
    ]
    add_table_grid(tech_headers, tech_rows)

    # ── 2.10 ──
    add_heading_2("2.10 Experimental Setup and Configuration")
    add_para(
        "All experiments are conducted on a local development workstation configured as follows.  The "
        "Apache Spark session is initialised in local[*] master mode, which allocates all available CPU "
        "cores to the Spark executor.  The driver process is allocated 2 GB of JVM heap memory, and "
        "columnar in-memory caching is enabled for iterative model training passes."
    )
    add_para(
        "The machine learning models use an 80/20 train-test stratified split with a fixed random seed "
        "(seed = 42) to ensure reproducibility across runs.  Hyperparameter tuning is performed via "
        "grid search over a predefined parameter lattice.  For the GBT regressor, the search space "
        "includes n_estimators in {50, 100, 200} and max_depth in {3, 5, 8}.  For the Random Forest "
        "classifier, the search covers n_estimators in {50, 100} and max_depth in {4, 6, 8}."
    )

    config_headers = ["Parameter", "Value"]
    config_rows = [
        ["Spark Master Mode", "local[*] (all CPU cores)"],
        ["Driver Memory", "2 GB"],
        ["Python Version", "3.14"],
        ["Train / Test Split", "80 / 20"],
        ["Random Seed", "42"],
        ["Dataset Size", "5 000 sessions"],
        ["Number of Stations", "10 municipal hubs"],
        ["Streaming Simulation", "50 events, 200 ms interval"],
    ]
    add_table_grid(config_headers, config_rows)

    # ── 2.11 ──
    add_heading_2("2.11 Evaluation Metrics")
    add_para(
        "The performance of each model is assessed using evaluation metrics that are standard in the "
        "machine learning literature and aligned with the university course rubric:"
    )

    add_heading_3("Regression Models (GBT Regressor, RF Regressor, Linear Regression)")
    add_para(
        "Root Mean Squared Error (RMSE):  Measures the square root of the average squared difference "
        "between predicted and actual values.  Lower values indicate better predictive accuracy.  "
        "RMSE is particularly sensitive to large errors, making it a strict performance indicator."
    )
    add_para(
        "Mean Absolute Error (MAE):  Computes the average absolute difference between predictions and "
        "ground truth.  Unlike RMSE, MAE treats all errors linearly and is therefore more robust to "
        "occasional outliers."
    )
    add_para(
        "Coefficient of Determination (R-squared):  Represents the proportion of variance in the "
        "target variable that is explained by the model.  An R-squared value of 1.0 indicates perfect "
        "prediction, while 0.0 indicates that the model performs no better than predicting the mean."
    )

    add_heading_3("Classification Model (Random Forest Classifier)")
    add_para(
        "Multi-class Accuracy:  The fraction of all predictions that match the true congestion label.\n\n"
        "Weighted Precision:  The average of per-class precision scores weighted by class frequency, "
        "measuring how many of the predicted positives are actually positive.\n\n"
        "Weighted Recall:  The average of per-class recall scores weighted by class frequency, "
        "measuring how many of the actual positives are correctly captured.\n\n"
        "Weighted F1-Score:  The harmonic mean of precision and recall, providing a single balanced "
        "metric for multi-class performance."
    )

    add_heading_3("Clustering Model (K-Means Spatial Clustering)")
    add_para(
        "Silhouette Score:  Ranges from \u22121 to +1, measuring how similar each data point is to its "
        "own cluster compared to the nearest neighbouring cluster.  A score near +1 indicates "
        "well-separated, compact clusters.\n\n"
        "Within-Set Sum of Squared Errors (WSSSE / Inertia):  The total squared Euclidean distance "
        "from each point to its assigned centroid.  Lower inertia indicates tighter clusters, though "
        "the metric naturally decreases as K increases and must be interpreted alongside the "
        "Silhouette Score."
    )

    add_para("")

    add_figure(os.path.join(DIAGRAM_DIR, "model_comparison.png"),
               "Figure 2.9: Model Evaluation Metrics \u2014 Preliminary Comparison")

    add_para(
        "The preliminary results from initial model training (detailed evaluation follows in Milestone 2, "
        "Chapter 4) are summarised below for reference:"
    )

    metric_headers = ["Model", "Module", "Key Metric", "Value"]
    metric_rows = [
        ["GBT Regressor", "Admin / Grid Load", "R\u00b2 Score", "0.7203"],
        ["RF Regressor", "Admin / Benchmark", "R\u00b2 Score", "0.7220"],
        ["RF Classifier", "Driver / Congestion", "F1-Score (Wtd)", "0.9491"],
        ["Linear Regression", "Driver / Duration", "R\u00b2 Score", "0.8282"],
        ["K-Means (K=4)", "Planner / Siting", "Silhouette Score", "0.6709"],
    ]
    add_table_grid(metric_headers, metric_rows)

    # ── Save ──
    doc.save(output_path)
    print(f"[Report Generator] Milestone 1 report saved to: {output_path}")
    return output_path


if __name__ == "__main__":
    create_report()
