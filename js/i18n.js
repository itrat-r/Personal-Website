// ============================================================
//  GERMAN TRANSLATIONS
//
//  English lives in index.html. Every element with
//  data-i18n="key" (text), data-i18n-label="key" (aria-label/title)
//  or data-i18n-alt="key" (image alt) is swapped to the matching
//  entry below when the visitor picks DE.
//  New text on the page? Add data-i18n="some.key" to it and
//  add "some.key" here.
// ============================================================
window.I18N_DE = {
  // header
  'skip': 'Zum Inhalt springen',
  'nav.impact': 'Wirkung',
  'nav.projects': 'Projekte',
  'nav.experience': 'Erfahrung',
  'nav.skills': 'Skills',
  'nav.contact': 'Kontakt',
  'theme': 'Hell-/Dunkelmodus umschalten',
  'close': 'Schließen',

  // hero
  'hero.eyebrow': '<span class="dot"></span> Offen für Data-Analyst-Stellen · Deutschland',
  'hero.hi': 'Hallo, ich bin <span class="hl">Itrat</span>.',
  'hero.turn': 'Ich mache aus chaotischen Daten',
  'hero.lead': '3,5 Jahre Erfahrung in Datenintegration und Pipeline-Entwicklung, dazu ein M.Sc. in Bioinformatik. Ich baue die ETL-Strecken, schreibe die Abfragen und liefere die Dashboards, damit Teams nicht mehr in Excel kopieren müssen.',
  'hero.cta': 'Meine Projekte ansehen →',
  'hero.cv': 'Lebenslauf herunterladen',
  'hero.pr': '🇩🇪 Niederlassungserlaubnis',
  'hero.en': 'Englisch · fließend',
  'pipe.etl': 'n8n · geplantes ETL',
  'pipe.s3': 'AWS S3 · verschlüsselt',
  'pipe.mongo': 'MongoDB · Aggregationen',
  'pipe.caption': 'Das Grundmuster fast aller meiner Projekte: <em>Quellen → Pipeline → Speicher → Erkenntnis</em>.',

  // impact
  'impact.title': '<span>01</span> Wirkung in Zahlen',
  'impact.years': 'Jahre',
  'impact.s1': 'in Datenintegration &amp; Pipeline-Entwicklung',
  'impact.s2': 'tägliche Uploads, verarbeitet mit MongoDB-Aggregation-Pipelines',
  'impact.s3': 'weniger Workflow-Fehler, seit Geschäftsanforderungen sauber in Integrationsanforderungen übersetzt werden',
  'impact.s4': 'manuelle Datenarbeit pro Woche durch automatisiertes ETL eingespart',
  'impact.s5': 'höhere Feature-Nutzung nach Usability- und A/B-Tests',
  'impact.s6': 'Teilnehmende an Usability-Tests, die Designentscheidungen geprägt haben',
  'console.run': '▶ Abfrage ausführen',
  'console.again': '↻ Erneut ausführen',
  'console.r1': 'Geplantes ETL (n8n) von OneDrive &amp; On-Premise in verschlüsseltes AWS S3 für 3 Enterprise-Kunden',
  'console.r2': 'MongoDB-Pipelines, die 500+ tägliche Uploads sauber und abfragbar halten',
  'console.r3': 'React- und MUI-Dashboards mit Live-KPIs statt manueller Excel-Berichte',
  'console.r4': '70 % weniger Workflow-Fehler durch präzisere Anforderungen mit Produkt &amp; Vertrieb',
  'console.rows': '4 Zeilen in 0,02 s zurückgegeben',

  // projects
  'projects.title': '<span>02</span> Datenprojekte',
  'projects.sub': 'Praxisprojekte, die ich Ihnen gern im Detail zeige. Klicken Sie auf eine Karte, um die Ergebnisse zu sehen.',
  'onco.desc': 'Somatische Mutationslandschaft einer Pan-Cancer-Kohorte mit 660 Fällen: Schema-Design, ETL, QC und Analyse in SQL, visualisiert mit Python.',
  'onco.result': 'BRAF V600E, TMB bei MSI-high und eine Kaplan-Meier-Überlebenskurve – alles in SQL berechnet.',
  'onco.more': 'Ergebnisse ansehen →',
  'onco.code': 'Code auf GitHub ↗',
  'onco.intro': '660 Fälle · 4 Tumorarten (Brust, Lunge, Darm, Melanom) · 2.590 Varianten-Calls. Abfragen in SQLite, Diagramme in Python (pandas + matplotlib) direkt aus der Datenbank. Synthetische Daten auf Basis publizierter Treiberhäufigkeiten und realer Hotspots.',
  'onco.codeLong': 'Code auf GitHub ansehen ↗',
  'onco.f1': '<strong>Varianten-QC-Trichter.</strong> 394 Calls mit geringer Lesetiefe und niedriger VAF (im Mittel 11× Tiefe, 2,5 % VAF) und 35 Pipeline-Duplikate werden vor der Analyse entfernt.',
  'onco.f2': '<strong>Treibergene.</strong> APC in 83 % der Darmtumoren, BRAF in 55 % der Melanome, PIK3CA und TP53 in etwa einem Drittel der Brustkrebsfälle.',
  'onco.f3': '<strong>Wiederkehrende Hotspots.</strong> BRAF V600E allein macht 78 % aller BRAF-Mutationen aus – typisch für ein aktivierendes Onkogen.',
  'onco.f4': '<strong>Tumormutationslast.</strong> MSI-high-Darmtumoren haben im Mittel 29,5 Mut/Mb gegenüber 3,1 bei MSS, und 96 % sind TMB-high: die Gruppe, die am ehesten auf Immuntherapie anspricht.',
  'onco.f5': '<strong>Gegenseitiger Ausschluss.</strong> BRAF–NRAS, EGFR–KRAS und PIK3CA–PTEN sind nie gemeinsam mutiert: Beide Gene liegen im selben Signalweg, ein Treffer genügt.',
  'onco.f6': '<strong>Überleben nach TP53-Status.</strong> Kaplan-Meier-Schätzer in reinem SQL: medianes Gesamtüberleben 36,0 Monate bei TP53-Mutation gegenüber 47,5 beim Wildtyp.',
  'onco.f7': '<strong>Rauchen und Lungenkrebs.</strong> EGFR-Mutationen bei 36 % der Nie-Raucher gegenüber 8 % der Raucher; bei KRAS ist es umgekehrt.',
  'onco.alt1': 'Varianten-QC-Trichter',
  'onco.alt2': 'Treibergene je Tumorart',
  'onco.alt3': 'Wiederkehrende Hotspots',
  'onco.alt4': 'Tumormutationslast',
  'onco.alt5': 'Gegenseitiger Ausschluss',
  'onco.alt6': 'Überleben nach TP53-Status',
  'onco.alt7': 'Rauchen und Lungenkrebs',

  // experience
  'exp.title': '<span>03</span> Erfahrung',
  'exp.c1': 'Geplante ETL-Pipelines (n8n) entworfen und automatisiert, die Cloud- (OneDrive) und On-Premise-Quellen verschlüsselt in AWS S3 integrieren – für 3 Enterprise-Kunden, mit ca. 5 Stunden Zeitersparnis pro Woche.',
  'exp.c2': 'MongoDB-Abfragen und Aggregation-Pipelines für 500+ tägliche Uploads geschrieben, die Produktfunktionen und interne Berichte speisen.',
  'exp.c3': 'Dashboards mit TypeScript, React und MUI gebaut, die Rohdaten in Nutzungsmetriken und KPIs verwandeln und manuelle Excel-Berichte ersetzen.',
  'exp.c4': 'Gemeinsam mit Produkt und Vertrieb Geschäftsanforderungen in Integrationsanforderungen übersetzt und Workflow-Fehler um 70 % reduziert.',
  'exp.i1': 'Eine plattformübergreifende Gesundheits-App für einen Enterprise-Kunden (React Native, Ionic, Figma) im agilen Team entworfen und entwickelt.',
  'exp.i2': 'Usability-Tests mit 50+ Teilnehmenden durchgeführt und die Ernährungsplan-Funktion per A/B-Test optimiert – 60 % höhere Feature-Nutzung.',
  'exp.ra': 'Wissenschaftliche Hilfskraft',
  'exp.bonn': 'Universität Bonn · Bonn',
  'exp.b1': 'Experimente mit 30+ Teilnehmenden durchgeführt, um menschliche Bewegungsdaten für das Training von Erkennungsmodellen zu erheben und zu annotieren.',
  'exp.b2': 'Bereinigungs-Pipelines in Python (Pandas) gebaut, die 1.000+ rohe Bewegungsbilder in modellfertige Datensätze verwandeln.',
  'exp.sra': 'Studentische Hilfskraft',
  'exp.mpi': 'Max-Planck-Institut für Informatik · Saarbrücken',
  'exp.m1': 'Interaktive Visualisierungstools und wissenschaftliche Web-Apps (JavaScript, React, Python) entwickelt, mit denen Forschende Computer-Vision-Datensätze erkunden konnten.',
  'edu.msc': 'M.Sc. Bioinformatik',
  'edu.uds': 'Universität des Saarlandes · 2016 – 2021',
  'edu.bsc': 'B.Sc. Bioinformatik',
  'edu.google': 'Coursera · laufend, Abschluss voraussichtlich 12/2026 · SQL (BigQuery), Tableau, R',
  'edu.german': '01/2026 – 08/2026 · berufsbezogenes Deutsch',

  // skills
  'skills.title': '<span>04</span> Werkzeugkasten',
  'skills.de': 'Data Engineering &amp; Analytics',
  'skills.ab': 'A/B-Tests',
  'skills.bi': 'BI &amp; Visualisierung',
  'skills.dash': 'Dashboard-Entwicklung',
  'skills.dev': 'Entwicklung &amp; Prozesse',
  'skills.lang': 'Sprachen',
  'skills.en': 'Englisch (fließend)',
  'skills.deu': 'Deutsch (B2)',

  // contact & footer
  'contact.title': 'Sie haben ein Datenproblem, das eine Pipeline braucht?',
  'contact.sub': 'Lassen Sie uns sprechen. Ich antworte schnell – auf Deutsch oder Englisch.',
  'footer': 'Erstellt mit HTML, CSS &amp; JS · Gehostet auf GitHub Pages',

  // typed headline words (array)
  'typed': ['Pipelines.', 'Dashboards.', 'Entscheidungen.', 'saubere Datensätze.', 'Antworten.']
};
