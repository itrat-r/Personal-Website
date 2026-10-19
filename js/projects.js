// ============================================================
//  YOUR PROJECTS: edit this list, the site renders it for you.
//
//  The entries below are PLACEHOLDERS with draft ideas. Replace
//  the text with your real projects (and real numbers!), then
//  set  draft: false  to remove the "draft" badge.
//
//  Fields:
//    title    – project name
//    emoji    – shown on the card thumbnail
//    colors   – two hex colors for the thumbnail gradient
//    summary  – 1–2 sentences: the question you answered
//    result   – the insight / impact (use a real number)
//    tags     – tools used; these become the filter buttons
//    links    – { code: "github url", demo: "live url", report: "url" }
//    draft    – true shows a "draft" badge
// ============================================================
window.PROJECTS = [
  {
    title: "Sales Performance Dashboard",
    emoji: "📊",
    colors: ["#1f4e8c", "#4aa3ff"],
    summary: "Interactive Power BI / Tableau dashboard answering which products and regions drive revenue, built from a public retail dataset.",
    result: "Replace with your key finding, e.g. 'Top 3 regions drive X% of revenue'.",
    tags: ["SQL", "Power BI", "Tableau"],
    links: { code: "", demo: "" },
    draft: true
  },
  {
    title: "Automated ETL Pipeline with n8n",
    emoji: "🔄",
    colors: ["#ff6b4a", "#ffb199"],
    summary: "Scheduled workflow pulling data from REST APIs, cleaning it and loading it into cloud storage. A public, anonymized version of the pipelines I build at work.",
    result: "Replace with e.g. hours saved per week or rows processed per run.",
    tags: ["n8n", "REST APIs", "AWS S3", "Python"],
    links: { code: "" },
    draft: true
  },
  {
    title: "A/B Test Analysis",
    emoji: "🧪",
    colors: ["#7a3fd1", "#c7a3ff"],
    summary: "Statistical analysis of an A/B experiment: sample size, significance testing and a clear ship / don't-ship recommendation.",
    result: "Replace with e.g. 'Variant B lifted conversion by X% (p = …)'.",
    tags: ["Python", "Pandas", "A/B testing"],
    links: { code: "", report: "" },
    draft: true
  },
  {
    title: "Exploratory Data Analysis Notebook",
    emoji: "🔍",
    colors: ["#118a6a", "#6fe3bd"],
    summary: "End-to-end EDA on a messy real-world dataset: cleaning, feature checks and visual storytelling in a Jupyter notebook.",
    result: "Replace with the most surprising thing you found.",
    tags: ["Python", "Pandas", "Data cleaning"],
    links: { code: "" },
    draft: true
  },
  {
    title: "MongoDB Aggregation Showcase",
    emoji: "🍃",
    colors: ["#2b7a3d", "#9be08f"],
    summary: "Collection of aggregation pipelines for usage analytics: grouping, windowing and reshaping documents into report-ready tables.",
    result: "Replace with e.g. query time before vs. after optimization.",
    tags: ["MongoDB", "NoSQL"],
    links: { code: "" },
    draft: true
  }
];
