/// ASCII chart generation for terminal output
/// Provides simple but effective visualizations for CLI usage

use std::collections::HashMap;

/// Generate a horizontal bar chart in ASCII
pub fn generate_bar_chart(data: &HashMap<String, usize>, title: &str, max_width: usize) -> String {
    if data.is_empty() {
        return format!("{}\n(No data to display)\n", title);
    }

    let mut output = String::new();
    output.push_str(&format!("{}\n", title));
    output.push_str(&"─".repeat(title.len()));
    output.push('\n');

    // Find the maximum value for scaling
    let max_value = *data.values().max().unwrap_or(&1);

    // Sort data by value (descending)
    let mut sorted_data: Vec<_> = data.iter().collect();
    sorted_data.sort_by(|a, b| b.1.cmp(a.1));

    // Find the maximum label length for alignment
    let max_label_len = sorted_data.iter()
        .map(|(label, _)| label.len())
        .max()
        .unwrap_or(0);

    for (label, value) in sorted_data {
        // Calculate bar length (leave room for label and value)
        let available_width = max_width.saturating_sub(max_label_len + 10);
        let bar_length = if max_value > 0 {
            ((*value as f64 / max_value as f64) * available_width as f64) as usize
        } else {
            0
        };

        // Create the bar
        let bar = if bar_length > 0 {
            "█".repeat(bar_length)
        } else {
            "▏".to_string() // Minimal bar for zero values
        };

        // Format the line
        output.push_str(&format!(
            "{:width$} │{:<bar_width$} {} ({})\n",
            label,
            bar,
            value,
            format_percentage(*value, data.values().sum()),
            width = max_label_len,
            bar_width = available_width
        ));
    }

    output.push('\n');
    output
}

/// Generate a complexity distribution chart
pub fn generate_complexity_chart(complexities: &[(String, u32)], max_width: usize) -> String {
    let mut output = String::new();
    output.push_str("🔥 Complexity Distribution\n");
    output.push_str("─────────────────────────\n");

    if complexities.is_empty() {
        output.push_str("(No functions analyzed)\n");
        return output;
    }

    let max_complexity = complexities.iter().map(|(_, c)| *c).max().unwrap_or(1);

    for (name, complexity) in complexities.iter().take(10) {
        let bar_length = ((*complexity as f64 / max_complexity as f64) * (max_width - 30) as f64) as usize;
        let bar = "█".repeat(bar_length.max(1));

        let risk_indicator = match *complexity {
            1..=5 => "🟢",
            6..=10 => "🟡",
            11..=20 => "🟠",
            _ => "🔴",
        };

        output.push_str(&format!(
            "{} {:20} │{:<width$} {}\n",
            risk_indicator,
            truncate_string(name, 20),
            bar,
            complexity,
            width = max_width - 30
        ));
    }

    output.push('\n');
    output
}

/// Generate a simple histogram for numerical data
pub fn generate_histogram(values: &[u32], title: &str, bins: usize, max_width: usize) -> String {
    let mut output = String::new();
    output.push_str(&format!("{}\n", title));
    output.push_str(&"─".repeat(title.len()));
    output.push('\n');

    if values.is_empty() {
        output.push_str("(No data to display)\n");
        return output;
    }

    let min_val = *values.iter().min().unwrap();
    let max_val = *values.iter().max().unwrap();

    if min_val == max_val {
        output.push_str(&format!("All values are: {}\n", min_val));
        return output;
    }

    // Create bins
    let bin_width = (max_val - min_val) as f64 / bins as f64;
    let mut bin_counts = vec![0; bins];

    for value in values {
        let bin_index = ((*value - min_val) as f64 / bin_width).floor() as usize;
        let bin_index = bin_index.min(bins - 1);
        bin_counts[bin_index] += 1;
    }

    let max_count = *bin_counts.iter().max().unwrap_or(&1);
    let chart_width = max_width - 20;

    for (i, count) in bin_counts.iter().enumerate() {
        let range_start = min_val + (i as f64 * bin_width) as u32;
        let range_end = min_val + ((i + 1) as f64 * bin_width) as u32;

        let bar_length = if max_count > 0 {
            ((*count as f64 / max_count as f64) * chart_width as f64) as usize
        } else {
            0
        };

        let bar = if bar_length > 0 {
            "█".repeat(bar_length)
        } else {
            "▏".to_string()
        };

        output.push_str(&format!(
            "{:2}-{:2} │{:<width$} ({})\n",
            range_start,
            range_end,
            bar,
            count,
            width = chart_width
        ));
    }

    output.push('\n');
    output
}

/// Generate a trend line using ASCII characters
pub fn generate_trend_line(values: &[f64], title: &str, max_width: usize) -> String {
    let mut output = String::new();
    output.push_str(&format!("{}\n", title));
    output.push_str(&"─".repeat(title.len()));
    output.push('\n');

    if values.is_empty() {
        output.push_str("(No data points)\n");
        return output;
    }

    if values.len() == 1 {
        output.push_str(&format!("Single value: {:.2}\n", values[0]));
        return output;
    }

    let height = 8;
    let width = max_width.min(values.len());
    let min_val = values.iter().fold(f64::INFINITY, |a, &b| a.min(b));
    let max_val = values.iter().fold(f64::NEG_INFINITY, |a, &b| a.max(b));

    if (max_val - min_val).abs() < f64::EPSILON {
        output.push_str(&format!("Constant value: {:.2}\n", min_val));
        return output;
    }

    // Create a 2D grid for the chart
    let mut chart = vec![vec![' '; width]; height];

    // Plot the values
    for (i, &value) in values.iter().enumerate().take(width) {
        let normalized = (value - min_val) / (max_val - min_val);
        let y = (normalized * (height - 1) as f64) as usize;
        let y = height.saturating_sub(1).min(height - 1 - y);
        chart[y][i] = '●';
    }

    // Draw connecting lines (simplified)
    for i in 0..width.saturating_sub(1) {
        let val1 = values[i];
        let val2 = values[i + 1];

        let y1 = height - 1 - ((val1 - min_val) / (max_val - min_val) * (height - 1) as f64) as usize;
        let y2 = height - 1 - ((val2 - min_val) / (max_val - min_val) * (height - 1) as f64) as usize;

        if y1 != y2 {
            let (start_y, end_y) = if y1 < y2 { (y1, y2) } else { (y2, y1) };
            for y in (start_y + 1)..end_y {
                if chart[y][i] == ' ' {
                    chart[y][i] = '│';
                }
            }
        }
    }

    // Output the chart
    output.push_str(&format!("Max: {:.2}\n", max_val));
    for row in chart {
        output.push_str("│");
        output.push_str(&row.iter().collect::<String>());
        output.push('\n');
    }
    output.push_str(&format!("└{}\n", "─".repeat(width)));
    output.push_str(&format!("Min: {:.2}\n", min_val));

    output.push('\n');
    output
}

/// Generate a summary box with key metrics
pub fn generate_summary_box(metrics: &HashMap<String, String>, title: &str) -> String {
    let mut output = String::new();

    // Calculate box width
    let content_width = metrics.iter()
        .map(|(k, v)| k.len() + v.len() + 3) // "key: value"
        .max()
        .unwrap_or(20)
        .max(title.len());

    let box_width = content_width + 4; // padding

    // Top border
    output.push_str(&format!("┌{}┐\n", "─".repeat(box_width - 2)));

    // Title
    output.push_str(&format!(
        "│ {:^width$} │\n",
        title,
        width = box_width - 4
    ));

    // Separator
    output.push_str(&format!("├{}┤\n", "─".repeat(box_width - 2)));

    // Content
    for (key, value) in metrics {
        output.push_str(&format!(
            "│ {}: {:>width$} │\n",
            key,
            value,
            width = box_width - key.len() - 6
        ));
    }

    // Bottom border
    output.push_str(&format!("└{}┘\n", "─".repeat(box_width - 2)));

    output
}

// Helper functions

fn format_percentage(value: usize, total: usize) -> String {
    if total == 0 {
        "0.0%".to_string()
    } else {
        format!("{:.1}%", (value as f64 / total as f64) * 100.0)
    }
}

fn truncate_string(s: &str, max_len: usize) -> String {
    if s.len() <= max_len {
        format!("{:<width$}", s, width = max_len)
    } else {
        format!("{}…", &s[..max_len.saturating_sub(1)])
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_bar_chart_generation() {
        let mut data = HashMap::new();
        data.insert("Rust".to_string(), 10);
        data.insert("JavaScript".to_string(), 5);
        data.insert("Python".to_string(), 3);

        let chart = generate_bar_chart(&data, "Language Usage", 50);

        assert!(chart.contains("Rust"));
        assert!(chart.contains("JavaScript"));
        assert!(chart.contains("Python"));
        assert!(chart.contains("Language Usage"));
    }

    #[test]
    fn test_complexity_chart_generation() {
        let complexities = vec![
            ("function1".to_string(), 15),
            ("function2".to_string(), 8),
            ("function3".to_string(), 3),
        ];

        let chart = generate_complexity_chart(&complexities, 60);

        assert!(chart.contains("function1"));
        assert!(chart.contains("🔴")); // High complexity indicator
        assert!(chart.contains("🟡")); // Medium complexity indicator
        assert!(chart.contains("🟢")); // Low complexity indicator
    }

    #[test]
    fn test_histogram_generation() {
        let values = vec![1, 2, 2, 3, 3, 3, 4, 4, 5];
        let histogram = generate_histogram(&values, "Value Distribution", 5, 40);

        assert!(histogram.contains("Value Distribution"));
        assert!(histogram.contains("█"));
    }

    #[test]
    fn test_summary_box_generation() {
        let mut metrics = HashMap::new();
        metrics.insert("Files".to_string(), "42".to_string());
        metrics.insert("Complexity".to_string(), "156".to_string());
        metrics.insert("Issues".to_string(), "3".to_string());

        let box_output = generate_summary_box(&metrics, "Project Summary");

        assert!(box_output.contains("Project Summary"));
        assert!(box_output.contains("Files"));
        assert!(box_output.contains("42"));
        assert!(box_output.contains("┌")); // Box drawing characters
        assert!(box_output.contains("└"));
    }
}