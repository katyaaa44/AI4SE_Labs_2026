# Software Requirements Specification

## Priority Scale

- **High:** Essential for core system operation or explicitly required by major stakeholders.
- **Medium:** Important functionality but not essential for the first usable version.
- **Low:** Optional, convenience, enhancement, or lower-impact functionality.

## Requirements

### REQ-001 — Material Volume Reports

**Priority:** High

**Sources:** `conversations/conv_pines014_material_volume.eml`, `conversations/conv_pines016_shelf_space.eml`, `early_draft_srs_galecia.txt`, `interview_cataloging_2009-05-08.txt`

**Description:** The system shall report material volume for an individual library or library system using applicable acquisitions, shelf, and circulation data, and support current and historical reporting. Reports shall provide configurable category breakdowns, including total items, holds, adult fiction, board books, fiction and non-fiction, and format; show counts by relevant item status; and support date-filtered acquisitions. The system shall support recurring board and assessment reporting without requiring manual assembly from unrelated screens. Branch managers shall participate in validation before the report is considered ready. Collection and circulation percentages by genre and format, including comparisons among libraries, system averages, and date ranges, are specified authoritatively in Capacity and Shelf-Space Analysis.

### REQ-002 — Capacity and Shelf-Space Analysis

**Priority:** High

**Sources:** `conversations/conv_pines015_capacity_interface.eml`, `conversations/conv_pines016_shelf_space.eml`, `early_draft_srs_galecia.txt`, `interview_cataloging_2009-05-08.txt`, `meeting_minutes/meeting_2009-03-15_minutes.txt`, `meeting_minutes/meeting_2009-07-20_minutes.txt`

**Description:** The system shall support analysis of branch capacity, collection distribution, and shelf-space utilization, including an all-branch overview and trends over time. Stakeholders shall select and document the capacity definition before capacity measures are implemented. The system shall estimate shelf space by genre and format using item dimensions or another documented proxy after investigating available data. This requirement is authoritative for computing and presenting collection and circulation percentages by genre and format, comparing those shares with estimated shelf-space shares, and comparing branches, system averages, and date ranges. The overview shall scale to the supported branch network and allow sorting, filtering, or grouping by relevant dimensions; users shall be able to drill down to branch details and export capacity data to CSV. Capacity status may be indicated with green, yellow, and red colors.

### REQ-003 — Batch Item Transfers

**Priority:** High

**Sources:** `conversations/conv_pines018_item_transfer.eml`, `early_draft_srs_galecia.txt`, `interview_cataloging_2009-05-08.txt`, `survey_results_2009.txt`

**Description:** The system shall provide an authorized utility to transfer selected items between branches or other locations in batches by updating their location records. Users shall be able to select candidates by query criteria, including item attributes, genre, and circulation history; manually include or exclude individual results; save and reuse or share queries; and select the destination. The workflow shall integrate with available query and report-template tools where applicable. It shall support pull lists, printable transit labels with item barcodes, a preview of item counts and source and destination locations, and explicit confirmation before changes are applied. Authorized users shall be able to undo transfers or restore original locations.

### REQ-004 — Transfer Reversion and Audit

**Priority:** High

**Sources:** `conversations/conv_pines018_item_transfer.eml`

**Description:** The system shall maintain item transfer history and record transfers in an audit record. It shall support scheduled or otherwise automated reversion of temporary transfers to original locations using configurable criteria, including elapsed time, completion of an event, checkout at the destination, or a configured status change. An item checked out at a mobile library shall remain there under the applicable rule, while an unused item may revert. Authorized users shall be able to review transfer history and identify transfer counts for a specified period. The system should notify relevant users about delays or transfer issues, with those conditions defined during implementation.

### REQ-005 — In-Transit Item Reporting

**Priority:** High

**Sources:** `conversations/conv_pines019_020_missing_intransit.eml`, `early_draft_srs_galecia.txt`, `interview_cataloging_2009-05-08.txt`, `meeting_minutes/meeting_2009-07-20_minutes.txt`

**Description:** The system shall provide a combined in-transit report for items traveling to and from locations, available at branch and system-wide scopes. Users shall be able to identify items that remain in transit beyond a configurable threshold, defaulting to seven days; an item shall be considered in transit when its arrival date is null and its departure date is earlier than the threshold. Transit records shall provide the necessary departure and arrival dates, and results shall be sortable by due date. The report shall support follow-up on long-transit items.

### REQ-006 — Missing, Damaged, and Claims-Returned Item Reports

**Priority:** High

**Sources:** `conversations/conv_pines019_020_missing_intransit.eml`, `early_draft_srs_galecia.txt`, `evergreen_reference_2009.txt`, `interview_cataloging_2009-05-08.txt`, `meeting_minutes/meeting_2009-07-20_minutes.txt`

**Description:** The system shall provide reports identifying missing and damaged items by branch, with date-range filtering and available item-condition notes. Missing items shall be identifiable through tracked statuses such as missing and lost. The system shall also support reporting on claims-returned items using applicable status data.

### REQ-007 — Record Deletion, Safeguards, and Audit

**Priority:** High

**Sources:** `conversations/conv_pines021_item_purging.eml`, `conversations/conv_pines022_deletions.eml`, `early_draft_srs_galecia.txt`, `interview_cataloging_2009-05-08.txt`, `survey_results_2009.txt`

**Description:** The system shall support authorized deletion of eligible records, including bibliographic records with no attached items and volume entries with associated copies. It shall require separate confirmation before deletion and safeguard against deleting an entire collection or the last copy within the relevant scope. Each completed deletion or purge shall be persistently auditable, including record type and identifier, user, date and time, and associated location; the audit shall capture status before deletion or a reason when available, and support reporting by date range, record type, user, location, and system. Where deletion requires a reason, the system shall prompt for one. Denied deletion attempts shall be recorded with the user, action, target when available, time, and reason when available. Users shall be able to schedule purge operations, subject to confirmation and safeguards. Audit data shall support review and troubleshooting, including reports that identify users with the highest deletion counts. Reporting interfaces shall be able to query the deletion audit data. These behaviors do not require database deletion triggers or any other particular implementation mechanism.

### REQ-008 — Purge Candidate Identification and Status Conversion

**Priority:** High

**Sources:** `conversations/conv_pines021_item_purging.eml`, `early_draft_srs_galecia.txt`, `interview_cataloging_2009-05-08.txt`

**Description:** The system shall provide read-only reports and utilities to identify records or items eligible for purging using configurable, combinable criteria, including status, time in status, last circulation, missing status for a configured number of months, and discard or weeding status. Criteria shall support logical AND combinations, and identifying candidates shall not delete records. The system shall provide a report to assist batch conversion of item statuses and support review and application of status changes to multiple selected items in a batch.

### REQ-009 — Last-Copy Reporting

**Priority:** High

**Sources:** `conversations/conv_pines021_item_purging.eml`, `early_draft_srs_galecia.txt`, `evergreen_reference_2009.txt`, `interview_cataloging_2009-05-08.txt`

**Description:** The system shall report items that are the only copy within a user-selected library, system, facility, or consortium scope, including deleted items that were last copies. The report shall provide information useful to catalogers reviewing corresponding external catalog entries, such as WorldCat, before editing or deleting records. WorldCat may be consulted as an external reference; a particular integration mechanism is not required.

### REQ-010 — Patron Demographic Reporting

**Priority:** High

**Sources:** `conversations/conv_pines023_patron_characteristics.eml`, `early_draft_srs_galecia.txt`, `evergreen_reference_2009.txt`, `meeting_minutes/meeting_2009-03-15_minutes.txt`, `meeting_minutes/meeting_2009-07-20_minutes.txt`, `survey_results_2009.txt`

**Description:** The system shall support patron reports and statistics grouped or filtered by age range, ZIP code, county, city, home branch, patron type, and preferred language. Users shall be able to combine multiple filters with AND and OR logic and report measures including patron counts and circulation or checkout counts. Age ranges shall be configurable and calculated at query time from birth date rather than relying on a stored age-range value. Required source fields shall be available, and records with missing optional demographic values shall remain included and identifiable as unavailable rather than silently excluded. Demographic statistics shall be anonymized before analysis and shall not include personally identifiable patron information.

### REQ-011 — Inactive Patron Reporting

**Priority:** High

**Sources:** `conversations/conv_pines024_inactive_patrons.eml`, `early_draft_srs_galecia.txt`, `evergreen_reference_2009.txt`

**Description:** The system shall generate inactive-patron reports based on the most recent qualifying circulation or electronic activity and a user-configurable number of preceding days, including commonly used periods of 30, 90, 180, and 365 days. Qualifying activity shall include online holds, online renewals, OPAC (Online Public Access Catalog) or patron-account logins, and logged access to integrated digital collections, using their respective data sources. Users shall be able to exclude specified categories such as opt-outs, do-not-disturb patrons, staff, or VIPs, and separately identify inactive patrons with outstanding fines. Reports shall support system, home-library, and county scopes; include current mailing addresses; and be exportable to CSV for outreach. Generation shall support background processing and caching for recurring use. An unquantified performance concern about approximately 3.5 million patrons is excluded pending measurable acceptance criteria, as documented in the blacklist.

### REQ-012 — Report Queue and Processing Controls

**Priority:** High

**Sources:** `conversations/conv_pines024_inactive_patrons.eml`, `early_draft_srs_galecia.txt`, `email_report_features.eml`, `evergreen_reference_2009.txt`, `interview_sysadmin_2009-05-10.txt`, `meeting_minutes/meeting_2009-07-20_minutes.txt`, `meeting_tech_subcommittee_2009-06-30.txt`, `survey_results_2009.txt`

**Description:** The system shall process long-running reports in the background and provide visibility into queued, running, completed, and failed reports, including queue position and submission time. Users shall be able to cancel scheduled or running reports, and processing shall respond to cancellation signals. The system shall support prioritizing reports in the queue. Report workloads shall be isolated from production operations sufficiently to avoid impairing OPAC and circulation services during operating and busy hours. A read-only replica may be used where configured. Measurable response-time and workload targets shall be established separately where required; this requirement does not assert an unquantified performance threshold.

### REQ-013 — Canonical Roles, Authentication, and Permissions

**Priority:** High

**Sources:** `early_draft_srs_galecia.txt`, `email_report_features.eml`, `email_staff_login.eml`, `evergreen_reference_2009.txt`, `interview_sysadmin_2009-05-10.txt`, `meeting_minutes/meeting_2009-07-20_minutes.txt`, `meeting_tech_subcommittee_2009-06-30.txt`, `survey_results_2009.txt`

**Description:** Canonical role terminology for this specification is Global System Administrator, Local Administrator, Library Manager, Department Head, Front Desk Staff, and Staff. OPAC means Online Public Access Catalog, the patron-facing interface. The system shall use assignable roles and security groups to control individual, workgroup, and staff access, with centrally managed permissions and scopes. Global System Administrators may administer system-wide roles, permissions, reporting configuration, and access; Local Administrators may administer local users, permissions, and reporting within their authorized organizational scope; Library Managers may access and run reports for their authorized library or libraries; Department Heads may access and run reports for their authorized department and scope; Front Desk Staff may access only the operational reports and data authorized for their assigned role; Staff may access only explicitly granted reports, datasets, and query functions. Administrators shall control access to reports, datasets, query tools, report creation, cloning, template modification, and available filters. Role changes shall update permissions automatically. Staff authentication shall support individual username-and-password login; optional card-swipe or RFID login may be provided without requiring specialized infrastructure, bypassing individual authentication, or removing password fallback. Audit records shall identify the individual staff member rather than only a shared terminal. Terminology pass: REQ-013, REQ-015, REQ-020, REQ-021, and REQ-024 use the canonical role labels and scope terminology; generic references to authorized administrators or users do not introduce additional roles.

### REQ-014 — Activity, Circulation, and Transaction Reporting

**Priority:** High

**Sources:** `early_draft_srs_galecia.txt`, `email_report_features.eml`, `evergreen_reference_2009.txt`, `interview_cataloging_2009-05-08.txt`, `survey_results_2009.txt`

**Description:** The system shall report and count circulation and other transactions individually and cumulatively, including check-ins, checkouts, renewals, holds placed and filled, fines collected, patron registrations, and transactions involving uncataloged materials. Reports shall distinguish applicable channels and types, including book-drop, terminal, staff, self-service, online, and OPAC activity; distinguish check-in timestamps from renewal timestamps; and exclude renewals from check-in date and time reports. Holds reports shall identify whether each hold was placed at a staff desk, public computer, or remotely. Users shall be able to group and cross-tabulate transactions by hour, terminal, branch, library system, patron age range, patron type, and patron location, and report relevant measures by patron, library, library group, system, or county. Reports shall support circulation comparisons across current, prior-month, and prior-year periods, usage counts by date range, and circulation behavior measures such as renewal likelihood, the percentage of checkouts that are renewals, statistics useful for understanding and predicting patron behavior and material use, and return speed.

### REQ-015 — Report Templates and Saved Definitions

**Priority:** High

**Sources:** `early_draft_srs_galecia.txt`, `email_report_features.eml`, `evergreen_reference_2009.txt`, `meeting_minutes/meeting_2009-03-15_minutes.txt`, `meeting_minutes/meeting_2009-07-20_minutes.txt`, `survey_results_2009.txt`

**Description:** The system shall provide canned reports, editable on-demand reports, open-template reports, and a web-based custom report writer. Global System Administrators and Local Administrators, within their authorized scopes, shall be able to create and share templates; authorized users shall run templates unchanged, modify permitted selections, save and reuse report definitions, and clone reports without changing originals. Administrators shall control which fields and filters users may alter and ensure modifications preserve required criteria and valid results. The system shall support shared report folders with permissions that allow or deny staff access to run specific reports, template management, canned report display options, predefined templates for board and executive reporting, Georgia Annual Report requirements, and identified system-wide needs. Users shall be able to combine selected canned reports into a single document, add canned reports subject to permissions, and access report descriptions, quick-access guidance, and hover tooltips for report titles. Reports shall show their name, selection criteria, and date criteria with results. Scheduling semantics and supported output formats are defined authoritatively in Report Scheduling and Output; this requirement does not redefine them. Access and permitted actions shall follow Canonical Roles, Authentication, and Permissions.

### REQ-016 — Project Roles, Report Coverage, and Specification Scope

**Priority:** Medium

**Sources:** `early_draft_srs_galecia.txt`, `email_report_features.eml`, `evergreen_reference_2009.txt`, `meeting_minutes/meeting_2009-03-15_minutes.txt`, `meeting_minutes/meeting_2009-07-20_minutes.txt`

**Description:** The reporting capability shall provide the report types and templates identified for operational, collection, executive, and board needs, including applicable Georgia Annual Report statistics. It shall support library management planning, patron demographic and interest analysis, staff workflow analysis, collection and inventory analysis, and financial oversight. The Reports Working Group shall review new report development and identify PINES-wide templates. Development shall be collaborative and iterative, with end-user prototype review. The requirements specification shall be readable by non-technical library audiences and sufficiently detailed for developers; it shall adapt relevant existing requirements to PINES needs and define capabilities for a future Evergreen release. Patrons may receive report-related information indirectly through library displays, not direct access to management reporting. Role terms follow Canonical Roles, Authentication, and Permissions.

### REQ-017 — Report Scheduling and Output

**Priority:** Medium

**Sources:** `early_draft_srs_galecia.txt`, `email_report_features.eml`, `evergreen_reference_2009.txt`, `meeting_tech_subcommittee_2009-06-30.txt`, `survey_results_2009.txt`

**Description:** The system shall allow reports to run immediately (ASAP) or be scheduled hourly, daily, weekly, monthly, or yearly, including recurring execution. Users shall be able to edit recurring report selections and recipients, cancel scheduled reports, and submit multiple reports together. Reports shall be deliverable through the web interface or email to designated addresses, with an optional address book. Supported output formats shall include CSV, HTML, and pivot-table output, with Excel supported where reliably available. Excel exports shall avoid unintended duplicate rows using consistently applied duplicate-handling rules. Users shall be able to upload values for filtering and select output formats when running or scheduling reports. These are the authoritative scheduling and output-format statements; other requirements shall refer to them rather than restating or modifying these semantics.

### REQ-018 — Financial Transaction and Account Reporting

**Priority:** High

**Sources:** `early_draft_srs_galecia.txt`, `email_financial_reports.eml`, `email_report_features.eml`

**Description:** The system shall track and support verification of fines, charges, waivers, payments, and e-commerce transactions, associating them with relevant patron and item records. Patron payment ledgers shall identify the charges to which payments were applied. Reports shall show fines and charges by type and period, waivers by period and branch, patron balances by patron, home library, and system, and payments by period, branch, and tender or collection channel, including cash, credit card, check, staff desk, self-check, and OPAC. Branches shall be able to view payments collected at their locations, and users shall be able to query accounts above a specified balance. Front-desk payments shall update associated financial information without delay. Financial records, reports, and archiving shall comply with applicable accounting, audit, privacy, and jurisdictional retention rules; designated audit data shall be retained for seven years unless applicable law requires a different configured period.

### REQ-019 — Data Architecture, Scale, and Environment Compatibility

**Priority:** High

**Sources:** `early_draft_srs_galecia.txt`, `evergreen_reference_2009.txt`, `interview_sysadmin_2009-05-10.txt`, `meeting_minutes/meeting_2009-07-20_minutes.txt`, `meeting_tech_subcommittee_2009-06-30.txt`

**Description:** The system shall operate with the specified relational ILS data structures and support complex relational reporting without requiring a denormalized reporting schema. Historical reporting shall not require a separate reporting warehouse; this architecture decision is authoritative and consistent with Transaction History and Privacy-Preserving Archives. The system shall be compatible with specified deployment environments, including Evergreen ILS 1.4.0.4, PostgreSQL 8.3, Linux or Solaris, and the specified Red Hat Enterprise Linux 5 and Solaris 10 SPARC environments where applicable. It shall support the stated consortium operating scale of 286 locations, 17 million annual circulations, and more than 900,000 items purchased or processed annually. Where browser-based access is provided, it shall support Internet Explorer 6.0 or later and Firefox 2.0 or later. Access shall be available through a web browser or Windows-compatible client. Enterprise infrastructure such as redundant servers, backups, and network connectivity may be relied upon as deployment dependencies.

### REQ-020 — Reporting Access, Data Sources, and Organization

**Priority:** High

**Sources:** `early_draft_srs_galecia.txt`, `meeting_minutes/meeting_2009-03-15_minutes.txt`, `meeting_minutes/meeting_2009-07-20_minutes.txt`, `meeting_tech_subcommittee_2009-06-30.txt`

**Description:** The system shall provide management and reporting tools for an enterprise integrated library system, centrally serving multiple locations and supporting authorized cross-branch and system-wide reporting. It shall use relevant ILS data, including acquisitions, cataloging, circulation, holds, OPAC, patron, financial, and staff data; reporting access to operational ILS data shall be read-only and shall not perform acquisitions or cataloging management. Management reporting shall remain separate from the patron-facing OPAC and shall not constrain OPAC functionality, although it may use OPAC-originated data and support indirect display of information to patrons through OPAC screens. The system shall support a Global System Administrator, Local Administrators, Library Managers, Department Heads, Front Desk Staff, and Staff in the scopes and permissions defined in Canonical Roles, Authentication, and Permissions. Data from locations shall be centrally reportable, with incomplete or outdated contributing data identifiable. Vendor exchanges shall use published APIs or automated standard-format files, including USMARC21 and EDIFACT where applicable; vendor data need not be available at every location.

### REQ-021 — Report Query Design and Data Selection

**Priority:** High

**Sources:** `early_draft_srs_galecia.txt`, `email_financial_reports.eml`, `email_report_features.eml`, `evergreen_reference_2009.txt`, `interview_cataloging_2009-05-08.txt`, `meeting_tech_subcommittee_2009-06-30.txt`, `survey_results_2009.txt`

**Description:** The system shall provide query and report-design tools for authorized users to select fields and values, use applicable picklists, set filters and ranges, and construct queries over supported record types and relationships. The report writer shall expose relevant database fields and support drag-and-drop field selection as well as other selection methods. Users shall be able to sort and filter results, upload text files of barcodes or TCNs as report-filter values, and retrieve MARC fields even when stored across multiple rows. Reports shall support Boolean AND and OR operations and regular-expression matching. Report data shall support documented relationships among bibliographic records, items, circulation transactions, patrons, debt records, holds, money records, staff, and accounts. Null or blank values shall not cause otherwise qualifying records to be omitted unless the user explicitly filters them out; this behavior shall be explicit and shall not depend merely on a database default. Users shall be able to filter survey responses by survey name, with the system resolving the selected name to its corresponding identifier internally. Report output formats and scheduling are governed by Report Scheduling and Output.

### REQ-022 — Transaction History and Privacy-Preserving Archives

**Priority:** High

**Sources:** `early_draft_srs_galecia.txt`, `email_report_features.eml`, `evergreen_reference_2009.txt`, `meeting_tech_subcommittee_2009-06-30.txt`, `survey_results_2009.txt`

**Description:** The system shall retain transaction history for a configurable period and retain monthly and annual aggregate transaction information indefinitely. Archived transactions used for demographic or statistical analysis shall protect patron privacy and omit personally identifiable information while preserving useful non-identifying statistics. Retention and anonymization shall comply with applicable state and local law. The system shall support current-data reporting and historical reporting as of a specified date or date range, including historical bills and values such as past shelving locations. Reports may run against current operational data; historical reporting does not require a separate reporting warehouse, as specified authoritatively in Data Architecture, Scale, and Environment Compatibility.

### REQ-023 — Operational, Collection, and Data-Quality Reports

**Priority:** Medium

**Sources:** `early_draft_srs_galecia.txt`, `email_financial_reports.eml`, `evergreen_reference_2009.txt`, `interview_cataloging_2009-05-08.txt`, `meeting_minutes/meeting_2009-07-20_minutes.txt`, `survey_results_2009.txt`

**Description:** The system shall provide on-demand and periodic operational, maintenance, collection-development, and data-quality reports. Supported reports shall include item creation dates and total-use counts; overdue items with patron contact information subject to permissions; inactive patron status; holds requiring purchase action, stale or unfilled holds, and items grouped by reason fines stopped; missing bibliographic fields; bibliographic records without items; invalid item types; long call numbers; records with holds; inactive items; items with holds in transit; last copies; and patrons with invalid home libraries. Reports shall support weeding and collection-development decisions, including last circulation date, item last-edit date independent of circulation, collection age and value by call number, item value based on purchase price, and values for the whole or selected collection. Additional reports shall include bibliographic and item edit counts, staff password-change dates, survey responses searchable by survey name, notices sent, and program attendance. Duration criteria shall be selectable or configurable where relevant. Output format and scheduling semantics follow Report Scheduling and Output.

### REQ-024 — Errors, Documentation, and System Feedback

**Priority:** Medium

**Sources:** `early_draft_srs_galecia.txt`, `meeting_minutes/meeting_2009-07-20_minutes.txt`, `meeting_tech_subcommittee_2009-06-30.txt`

**Description:** The system shall provide users with high-level error feedback and provide administrators with query-specific diagnostic feedback, including the affected table, field, and error type where available. The developer shall provide complete data specifications, including field names, data types, and relationships, for records maintained or accessed by management processes, and high-level process documentation covering major workflows such as bibliographic import and export, authority validation, and standard reports. Any role-specific actions shall use the canonical roles and scopes defined in Canonical Roles, Authentication, and Permissions.

### REQ-025 — Accessibility, HTML, and Online Help

**Priority:** High

**Sources:** `early_draft_srs_galecia.txt`, `evergreen_reference_2009.txt`, `interview_sysadmin_2009-05-10.txt`, `meeting_minutes/meeting_2009-07-20_minutes.txt`, `meeting_tech_subcommittee_2009-06-30.txt`

**Description:** The system and its reporting workflows shall comply with applicable Section 508 accessibility requirements and support screen readers, screen magnification, and other assistive technologies, including JAWS, NVDA, and ZoomText. Non-text content shall have appropriate alternative text and ARIA labels where needed. Web pages, report output, and online help shall produce standards-compliant HTML. Online help shall be available within the system, searchable, hierarchical, and cross-linked, and provide guidance relevant to system functions and reporting workflows.

### REQ-026 — Development, Training, and Configuration Promotion

**Priority:** Medium

**Sources:** `early_draft_srs_galecia.txt`, `evergreen_reference_2009.txt`, `interview_sysadmin_2009-05-10.txt`, `meeting_minutes/meeting_2009-07-20_minutes.txt`, `meeting_tech_subcommittee_2009-06-30.txt`

**Description:** The system shall provide separate development, training, and production environments. Training activities shall not put production data at risk, and development and training configurations shall be promotable to production. The system shall support exporting and importing applicable templates, permissions, saved queries, and other configuration between environments without requiring manual recreation.

### REQ-027 — Uncataloged Material Inventory and Usage

**Priority:** Medium

**Sources:** `early_draft_srs_galecia.txt`, `interview_cataloging_2009-05-08.txt`

**Description:** The system shall support inventory, distribution, and usage tracking for uncataloged materials, including paperbacks and children's board books, without requiring an individual catalog record for every item. Workflows shall support efficient processing and distribution with reduced branch staff effort, and recorded usage shall be available for reporting and included in relevant circulation statistics.

## Blacklist

### BL-001 — Report-Separation Documentation Instruction

**Original requirement:** Source: conversations/conv_pines019_020_missing_intransit.eml; candidate text: “Treat missing/damaged and in-transit reports as two separate but related requirements.”

**Sources:** `conversations/conv_pines019_020_missing_intransit.eml`

**Reason:** This is a specification-organization instruction, not software behavior. The missing/damaged report and in-transit report capabilities are separately retained in accepted requirements. Remediation: keep the separation in requirements documentation, not as a product requirement.

### BL-002 — Unresolved Cleanup Automation Choice

**Original requirement:** Source: conversations/conv_pines021_item_purging.eml; candidate text: the cleanup operation for deleting volumes with copies and records with no items “may be automated or manual.”

**Sources:** `conversations/conv_pines021_item_purging.eml`

**Reason:** The candidate explicitly leaves the execution approach undecided, so it cannot establish a verifiable workflow or automation requirement. Deletion capabilities are retained without assuming either approach. Remediation: specify and validate the workflow only if stakeholders later select one.

### BL-003 — Named Weeding-Season Testers

**Original requirement:** Source: conversations/conv_pines021_item_purging.eml; candidate text: test the system during weeding season by named individuals.

**Sources:** `conversations/conv_pines021_item_purging.eml`

**Reason:** This specifies a project test activity and personnel rather than delivered system behavior. Remediation: manage it in the verification or project test plan.

### BL-004 — Database Trigger Implementation

**Original requirement:** Source: conversations/conv_pines022_deletions.eml; candidate text: “Use database deletion triggers to write deletion events to an audit table.”

**Sources:** `conversations/conv_pines022_deletions.eml`

**Reason:** This prescribes a database implementation mechanism without evidence that triggers are necessary. The required audit behavior is accepted independently of implementation. Remediation: retain the mechanism, if selected, in architecture or design documentation rather than the product requirements.

### BL-005 — Unspecified Report Performance Target

**Original requirement:** Source: conversations/conv_pines024_inactive_patrons.eml; excerpt: “for 3.5 million patrons, this query could be slow.” Candidate summary: the solution should account for approximately 3.5 million patrons without unacceptable report-query performance.

**Sources:** `conversations/conv_pines024_inactive_patrons.eml`

**Reason:** The candidate supplies no measurable response-time or throughput target, concurrency level, workload definition, or hardware baseline, so “could be slow” cannot be verified as a performance requirement. It is excluded pending measurable stakeholder-defined acceptance criteria. Remediation: if stakeholders provide dataset size, response-time or throughput targets, concurrency, and hardware baseline, convert this into a measurable non-functional requirement and remove this blacklist disposition.

### BL-006 — Ease of Updating Financial Information

**Original requirement:** Source: early_draft_srs_galecia.txt; candidate text: “Financial information shall be easy to update.”

**Sources:** `early_draft_srs_galecia.txt`

**Reason:** “Easy” is subjective and the candidate identifies no information, authorized user, task, or usability acceptance criterion. Concrete financial tracking and reporting capabilities are accepted separately. Remediation: define the specific update tasks and measurable usability criteria before adding a usability requirement.

### BL-007 — Report Output Testing and Proof

**Original requirement:** Source: early_draft_srs_galecia.txt; candidate text: report output shall be “tested and proven.”

**Sources:** `early_draft_srs_galecia.txt`

**Reason:** The candidate defines neither a test method nor an acceptance criterion for what counts as tested or proven; it describes verification activity, not product behavior. Remediation: place the verification method and evidence requirements in the test plan.

### BL-008 — Ease of Report Permission Administration

**Original requirement:** Source: early_draft_srs_galecia.txt; candidate text: “Report permissions must be easy to administer.”

**Sources:** `early_draft_srs_galecia.txt`

**Reason:** The candidate provides no defined administration tasks or measurable usability criteria. Concrete role and permission capabilities are accepted separately. Remediation: specify the administrative tasks and measurable usability threshold if this quality requirement is needed.

### BL-009 — Unspecified Open-Hours Performance Goal

**Original requirement:** Source: early_draft_srs_galecia.txt; candidate text: searches and reports shall run during open hours without disrupting other system functions.

**Sources:** `early_draft_srs_galecia.txt`

**Reason:** The candidate gives no defined workload, response-time threshold, or measurable limit for disruption. Report workload isolation is retained in Report Queue and Processing Controls, but this candidate does not supply a verifiable performance target. Remediation: define workload and service-level thresholds before adding a performance acceptance criterion.

### BL-010 — Unspecified Boolean Operator Set

**Original requirement:** Source: early_draft_srs_galecia.txt; candidate text: the query tool shall support the “full range” of Boolean operators.

**Sources:** `early_draft_srs_galecia.txt`

**Reason:** “Full range” does not identify the required operators or their semantics. Explicit AND and OR behavior is retained in Report Query Design and Data Selection. Remediation: specify any additional operators and their semantics if they are required.

### BL-011 — Unspecified Aged-Debt Report Enhancement

**Original requirement:** Source: evergreen_reference_2009.txt; candidate text: provide an “enhanced detailed aged-debt report.”

**Sources:** `evergreen_reference_2009.txt`

**Reason:** The candidate does not state what enhancement or report fields are required, so it cannot be specified or verified. Remediation: identify the needed fields, filters, calculations, and output behavior before creating a requirement.

### BL-012 — Iterative Specification Methodology

**Original requirement:** Source: meeting_minutes/meeting_2009-03-15_minutes.txt; candidate text: develop detailed user-interface and data-structure specifications later using an iterative, prototype-oriented methodology.

**Sources:** `meeting_minutes/meeting_2009-03-15_minutes.txt`

**Reason:** This prescribes a requirements-development process, not delivered software behavior or a product constraint. Remediation: manage the methodology in the project plan.

### BL-013 — Coordination with Separate Module Specifications

**Original requirement:** Source: meeting_minutes/meeting_2009-03-15_minutes.txt; candidate text: coordinate report requirements with separate Acquisitions and Cataloging module specifications.

**Sources:** `meeting_minutes/meeting_2009-03-15_minutes.txt`

**Reason:** This is a project coordination dependency without a defined, verifiable system behavior or interface. Remediation: track coordination in project management; specify any resulting interface as a software requirement if needed.

### BL-014 — Reports Mission Statement

**Original requirement:** Source: meeting_minutes/meeting_2009-03-15_minutes.txt; candidate text: provide optimal Reports functionality for PINES management processes and define associated software requirements.

**Sources:** `meeting_minutes/meeting_2009-03-15_minutes.txt`

**Reason:** This is a broad mission statement with a subjective goal and no testable behavior. Specific report capabilities are retained elsewhere. Remediation: translate any remaining stakeholder need into a functional or measurable quality requirement.

### BL-015 — Requirements-Effort Scope

**Original requirement:** Source: meeting_minutes/meeting_2009-03-15_minutes.txt; candidate text: the initial requirements effort shall focus on functional requirements rather than detailed user-interface specifications.

**Sources:** `meeting_minutes/meeting_2009-03-15_minutes.txt`

**Reason:** This limits the scope of requirements work and does not define a delivered-system capability or quality constraint. Remediation: record it in the project scope or requirements-management plan.

### BL-016 — Tentative Separate Reporting Warehouse

**Original requirement:** Source: meeting_tech_subcommittee_2009-06-30.txt; candidate text: the system may require a reporting warehouse to support historical reporting.

**Sources:** `meeting_tech_subcommittee_2009-06-30.txt`

**Reason:** The statement is tentative and conflicts with the accepted architecture decision that historical reporting does not require a separate reporting warehouse. Historical reporting remains required without mandating a warehouse. Remediation: revise the architecture decision only if stakeholders formally change the constraint and reconcile the related requirements.

### BL-017 — Unspecified Usability Evaluation Criteria

**Original requirement:** Source: survey_results_2009.txt; candidate text: the reporting interface shall enable users to find and use needed reports, with usability measures defined during design.

**Sources:** `survey_results_2009.txt`

**Reason:** The candidate defers all acceptance criteria and provides no presently verifiable usability requirement. Remediation: define observable tasks and measurable usability thresholds before adopting a usability requirement.

## Quality Review

**Status:** FAIL after the maximum of 3 review attempts.

The document contains the best available refinement, but the reviewer reported these remaining issues:

- Remove or reconcile the reporting-warehouse contradiction: decide whether the system MAY use a separate historical reporting warehouse or whether historical reporting MUST NOT require one. Then update artifacts consistently: if the authoritative decision is 'no separate warehouse' (as currently in REQ-019), remove candidate CAND-420 ('The system shall provide a historical reporting warehouse') from any requirement candidate_ids (specifically remove CAND-420 from REQ-022 candidate_ids). Alternatively, if stakeholders want to allow/require a reporting warehouse, change REQ-019 text to permit an optional/conditional warehouse and explicitly document the conditions under which a warehouse is required. Do one of the two and keep the decision consistent across REQ-019, REQ-022, REQ-022 candidate_ids, and blacklist BL-016.
- Address BL-016 (Tentative Separate Reporting Warehouse) and CAND-420: BL-016 currently lists only CAND-645. If you intend to exclude 'reporting warehouse' claims, add CAND-420 to BL-016 (update the blacklist entry text and candidate_ids). If instead you accept a warehouse as an option, remove BL-016 or update it so it no longer blacklists the warehouse candidates.
- Remove the blacklisted performance candidate (CAND-169) from REQ-011 candidate_ids and from the REQ-011 description. BL-005 intentionally excludes that unquantified performance assertion; either convert it to a measurable non-functional requirement (stakeholders must provide dataset size, response-time targets, concurrency levels, and hardware baseline) or keep it blacklisted. DO NOT leave CAND-169 referenced inside REQ-011 candidate_ids in the final catalog. If the performance requirement is to be accepted later, replace the blacklisted candidate with a new measurable performance requirement ID and update REQ-011 accordingly.
- Ensure blacklist entries are not referenced as accepted content anywhere: for every blacklist entry (BL-001 .. BL-017), remove the associated candidate_ids from the requirements candidate_ids lists if they appear. Concretely, verify and remove the following candidate IDs from any requirement candidate_ids lists (these are the candidate_ids referenced by the provided blacklist entries): CAND-084, CAND-094, CAND-098, CAND-120, CAND-169, CAND-188, CAND-208, CAND-210, CAND-217, CAND-235, CAND-427, CAND-536, CAND-537, CAND-538, CAND-539, CAND-645, CAND-676. If any of these are present in requirement candidate lists, remove them or move them to an accepted/modified requirement with a clear, testable statement.
- De-duplicate and clarify architecture-level statements: REQ-019 (Data Architecture) is the authoritative architectural statement about historical reporting and reporting schema. Remove overlapping architecture-language from REQ-022 and other mid-level requirements and instead cross-reference REQ-019. For example, strip 'this architecture decision is authoritative' style language out of non-architecture requirements and add cross-reference phrases (e.g., 'See REQ-019 for authoritative architecture on reporting warehouse decisions').
- Normalize role and scope terminology across all requirements: run a text normalization pass and replace all role variants (e.g., 'Global Admin', 'Global Admin role', 'Local Admin') with the canonical labels defined in REQ-013: 'Global System Administrator', 'Local Administrator', 'Library Manager', 'Department Head', 'Front Desk Staff', and 'Staff'. Update any requirement text and candidate lists that use alternative labels. Specifically check REQ-015, REQ-016, REQ-020, REQ-021, REQ-024 and any other requirements for non-canonical role tokens and normalize them.
- Remove implementation-prescriptive statements from functional requirements: ensure that any candidate that prescribes an implementation mechanism (for example, BL-004's original CAND-120 suggesting 'use database deletion triggers') is not included as an accepted functional requirement. If the audit behavior is required, retain the audit behavior but remove the implementation detail; move implementation specifics to architecture/design documentation. Concretely, ensure CAND-120 is not present in requirement candidate lists (it currently appears in BL-004) and that REQ-007 does not prescribe triggers as the implementation method.
- Consolidate overlapping reporting/warehouse/historical-reporting language between REQ-019 and REQ-022: after deciding the authoritative architecture stance, update REQ-022 to remove any wording that contradicts REQ-019. If REQ-019 remains authoritative that 'historical reporting does not require a separate reporting warehouse', edit REQ-022 description to state: 'Historical reporting shall be supported as specified in REQ-019; a separate reporting warehouse is not required but may be used if the deployment architecture chooses to include one.'
- Run a final pass to ensure no blacklisted candidate_ids remain in any requirement candidate_ids arrays: after applying the preceding corrections, produce a diff listing all candidate_ids removed from requirements because they are blacklisted (so reviewers can verify).
- Confirm that the requirements' source traceability remains intact after edits: if any requirement loses a source document mention while removing blacklisted candidates or normalizing text, reassign appropriate source documents or add an explicit rationale for exclusion so the source_documents list remains fully covered.
