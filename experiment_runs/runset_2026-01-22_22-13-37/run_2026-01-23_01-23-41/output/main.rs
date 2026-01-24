use clap::{App, Arg, SubCommand};
use std::path::PathBuf;
use walkdir::WalkDir;

mod code_analyzer;
use code_analyzer::{CodeAnalyzer, AnalysisResult};

fn main() {
    let matches = App::new("Code Analyzer")
        .version("0.1.0")
        .about("A powerful code analysis tool using tree-sitter for robust parsing")
        .arg(
            Arg::with_name("input")
                .help("Input file or directory to analyze")
                .required(true)
                .index(1),
        )
        .arg(
            Arg::with_name("format")
                .short("f")
                .long("format")
                .value_name("FORMAT")
                .help("Output format: json, table, summary")
                .takes_value(true)
                .default_value("summary"),
        )
        .arg(
            Arg::with_name("recursive")
                .short("r")
                .long("recursive")
                .help("Recursively analyze directories"),
        )
        .arg(
            Arg::with_name("language")
                .short("l")
                .long("language")
                .value_name("LANG")
                .help("Force specific language (rust, javascript, typescript, python, go)")
                .takes_value(true),
        )
        .subcommand(
            SubCommand::with_name("complexity")
                .about("Focus on cyclomatic complexity analysis")
                .arg(
                    Arg::with_name("threshold")
                        .short("t")
                        .long("threshold")
                        .value_name("NUMBER")
                        .help("Complexity threshold for warnings")
                        .takes_value(true)
                        .default_value("10"),
                ),
        )
        .subcommand(
            SubCommand::with_name("dependencies")
                .about("Analyze import/dependency patterns")
        )
        .subcommand(
            SubCommand::with_name("metrics")
                .about("Generate comprehensive code metrics")
        )
        .get_matches();

    let input_path = PathBuf::from(matches.value_of("input").unwrap());
    let format = matches.value_of("format").unwrap();
    let recursive = matches.is_present("recursive");

    let mut analyzer = CodeAnalyzer::new();

    match analyze_path(&mut analyzer, &input_path, recursive) {
        Ok(results) => {
            match matches.subcommand() {
                ("complexity", Some(sub_matches)) => {
                    let threshold = sub_matches
                        .value_of("threshold")
                        .unwrap()
                        .parse::<u32>()
                        .unwrap_or(10);
                    display_complexity_report(&results, threshold);
                }
                ("dependencies", _) => {
                    display_dependency_report(&results);
                }
                ("metrics", _) => {
                    display_metrics_report(&results);
                }
                _ => {
                    display_results(&results, format);
                }
            }
        }
        Err(e) => {
            eprintln!("Analysis failed: {:?}", e);
            std::process::exit(1);
        }
    }
}

fn analyze_path(
    analyzer: &mut CodeAnalyzer,
    path: &PathBuf,
    recursive: bool,
) -> Result<Vec<(PathBuf, AnalysisResult)>, Box<dyn std::error::Error>> {
    let mut results = Vec::new();

    if path.is_file() {
        let result = analyzer.analyze_file(path)?;
        results.push((path.clone(), result));
    } else if path.is_dir() {
        let walker = if recursive {
            WalkDir::new(path).into_iter()
        } else {
            WalkDir::new(path).max_depth(1).into_iter()
        };

        for entry in walker.filter_map(|e| e.ok()) {
            let path = entry.path();
            if path.is_file() && is_supported_file(path) {
                match analyzer.analyze_file(path) {
                    Ok(result) => results.push((path.to_path_buf(), result)),
                    Err(e) => eprintln!("Warning: Failed to analyze {}: {:?}", path.display(), e),
                }
            }
        }
    }

    Ok(results)
}

fn is_supported_file(path: &std::path::Path) -> bool {
    if let Some(extension) = path.extension().and_then(|ext| ext.to_str()) {
        matches!(extension, "rs" | "js" | "ts" | "py" | "go")
    } else {
        false
    }
}

fn display_results(results: &[(PathBuf, AnalysisResult)], format: &str) {
    match format {
        "json" => display_json_results(results),
        "table" => display_table_results(results),
        "summary" | _ => display_summary_results(results),
    }
}

fn display_summary_results(results: &[(PathBuf, AnalysisResult)]) {
    println!("🔍 Code Analysis Summary");
    println!("========================");

    let total_files = results.len();
    let total_functions: usize = results.iter().map(|(_, r)| r.functions.len()).sum();
    let total_types: usize = results.iter().map(|(_, r)| r.types.len()).sum();

    println!("📊 Overall Statistics:");
    println!("  Files analyzed: {}", total_files);
    println!("  Total functions: {}", total_functions);
    println!("  Total types: {}", total_types);
    println!();

    for (path, result) in results {
        println!("📄 {}", path.display());
        println!("  Language: {}", result.language);
        println!("  Functions: {}", result.functions.len());
        println!("  Types: {}", result.types.len());
        println!("  Imports: {}", result.imports.len());

        if !result.functions.is_empty() {
            let avg_complexity: f64 = result.functions.iter()
                .map(|f| f.complexity as f64)
                .sum::<f64>() / result.functions.len() as f64;
            println!("  Avg Complexity: {:.1}", avg_complexity);
        }
        println!();
    }
}

fn display_table_results(results: &[(PathBuf, AnalysisResult)]) {
    println!("{:<40} {:<12} {:<10} {:<8} {:<8}", "File", "Language", "Functions", "Types", "Imports");
    println!("{}", "-".repeat(80));

    for (path, result) in results {
        let file_name = path.file_name()
            .and_then(|n| n.to_str())
            .unwrap_or("unknown");

        println!(
            "{:<40} {:<12} {:<10} {:<8} {:<8}",
            file_name,
            result.language,
            result.functions.len(),
            result.types.len(),
            result.imports.len()
        );
    }
}

fn display_json_results(results: &[(PathBuf, AnalysisResult)]) {
    // In a real implementation, we'd use serde_json here
    println!("{{");
    println!("  \"analysis_results\": [");

    for (i, (path, result)) in results.iter().enumerate() {
        println!("    {{");
        println!("      \"file\": \"{}\",", path.display());
        println!("      \"language\": \"{}\",", result.language);
        println!("      \"functions\": {},", result.functions.len());
        println!("      \"types\": {},", result.types.len());
        println!("      \"imports\": {}", result.imports.len());

        if i < results.len() - 1 {
            println!("    }},");
        } else {
            println!("    }}");
        }
    }

    println!("  ]");
    println!("}}");
}

fn display_complexity_report(results: &[(PathBuf, AnalysisResult)], threshold: u32) {
    println!("🔥 Complexity Analysis (threshold: {})", threshold);
    println!("=====================================");

    let mut high_complexity_functions = Vec::new();

    for (path, result) in results {
        for func in &result.functions {
            if func.complexity > threshold {
                high_complexity_functions.push((path, func));
            }
        }
    }

    if high_complexity_functions.is_empty() {
        println!("✅ No functions exceed the complexity threshold!");
    } else {
        println!("⚠️  Functions exceeding complexity threshold:");
        println!();

        for (path, func) in high_complexity_functions {
            println!("📍 {}:{}", path.display(), func.line_start);
            println!("  Function: {}", func.name);
            println!("  Complexity: {} (threshold: {})", func.complexity, threshold);
            println!("  Parameters: {}", func.parameters.len());
            println!();
        }
    }
}

fn display_dependency_report(results: &[(PathBuf, AnalysisResult)]) {
    println!("📦 Dependency Analysis");
    println!("====================");

    let mut import_frequency = std::collections::HashMap::new();

    for (_, result) in results {
        for import in &result.imports {
            *import_frequency.entry(import.module.clone()).or_insert(0) += 1;
        }
    }

    let mut sorted_imports: Vec<_> = import_frequency.iter().collect();
    sorted_imports.sort_by_key(|(_, count)| std::cmp::Reverse(**count));

    println!("Most frequently imported modules:");
    for (module, count) in sorted_imports.iter().take(10) {
        println!("  {:<30} (used {} times)", module, count);
    }
}

fn display_metrics_report(results: &[(PathBuf, AnalysisResult)]) {
    println!("📈 Comprehensive Metrics");
    println!("=======================");

    let total_functions: usize = results.iter().map(|(_, r)| r.functions.len()).sum();
    let total_types: usize = results.iter().map(|(_, r)| r.types.len()).sum();
    let total_imports: usize = results.iter().map(|(_, r)| r.imports.len()).sum();

    println!("Overall Statistics:");
    println!("  Total Files: {}", results.len());
    println!("  Total Functions: {}", total_functions);
    println!("  Total Types: {}", total_types);
    println!("  Total Imports: {}", total_imports);

    if total_functions > 0 {
        let complexities: Vec<u32> = results
            .iter()
            .flat_map(|(_, r)| r.functions.iter().map(|f| f.complexity))
            .collect();

        let avg_complexity = complexities.iter().sum::<u32>() as f64 / complexities.len() as f64;
        let max_complexity = *complexities.iter().max().unwrap_or(&0);

        println!("  Average Function Complexity: {:.2}", avg_complexity);
        println!("  Maximum Function Complexity: {}", max_complexity);
    }

    // Language breakdown
    let mut language_stats = std::collections::HashMap::new();
    for (_, result) in results {
        *language_stats.entry(result.language.clone()).or_insert(0) += 1;
    }

    println!("\nLanguage Distribution:");
    for (lang, count) in language_stats {
        println!("  {}: {} files", lang, count);
    }
}