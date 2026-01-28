# 🔍 Code Analysis Visualization Tool

**A Collaborative Creation by Alice & Bob**

An interactive web-based tool for analyzing Python code complexity and structure with beautiful visualizations. This project demonstrates the power of AI pair programming, combining AST analysis, complexity metrics, and modern web visualization.

![Python](https://img.shields.io/badge/Python-3.7%2B-blue)
![JavaScript](https://img.shields.io/badge/JavaScript-ES6%2B-yellow)
![HTML5](https://img.shields.io/badge/HTML5-Modern-orange)
![License](https://img.shields.io/badge/License-MIT-green)

## ✨ Features

### 🧠 **Advanced Code Analysis**
- **AST Parsing**: Deep structural analysis of Python code
- **Complexity Metrics**: Cyclomatic and cognitive complexity calculations
- **Function Analysis**: Detailed metrics for every function including nesting depth
- **Class Detection**: Inheritance mapping and method extraction
- **Import Dependencies**: Complete dependency graph visualization

### 📊 **Interactive Visualizations**
- **Complexity Distribution**: Doughnut charts showing complexity levels
- **Function Metrics**: Bar charts comparing different complexity measures
- **Code Structure**: Pie charts of functions, classes, and imports
- **Dependency Analysis**: Horizontal bar charts of import relationships
- **Detailed Function List**: Sortable, searchable function details with complexity ratings

### 🌐 **Modern Web Interface**
- **Responsive Design**: Works on desktop and mobile devices
- **Real-time Analysis**: Upload Python files for instant analysis
- **Beautiful UI**: Gradient backgrounds, smooth animations, and modern styling
- **Interactive Charts**: Built with Chart.js for smooth, professional visualizations
- **Error Handling**: Graceful fallbacks and informative error messages

## 🚀 Quick Start

### **Option 1: Easy Launch (Recommended)**
```bash
python3 output/launch_visualizer.py
```
This will:
- Start the web server on `http://localhost:8080`
- Create a demo file for testing
- Automatically open your browser
- Provide usage instructions

### **Option 2: Manual Launch**
```bash
# Start the server
python3 output/visualization_server.py

# Open your browser to
http://localhost:8080
```

## 📁 Project Structure

```
code-analysis-visualization/
├── output/
│   ├── 📄 web_interface.html          # Modern web UI with interactive charts
│   ├── 🐍 visualization_server.py     # Python web server with REST API
│   ├── 🚀 launch_visualizer.py        # Easy launcher script
│   └── 📊 demo_complexity_code.py     # Sample code for testing (auto-generated)
├── 📖 README.md                       # This documentation
├── 🔍 ast_analyzer.py                 # AST-based code structure analyzer (Bob's creation)
└── 📈 complexity_analyzer.py          # Complexity calculator (Bob's creation)
```

## 🔧 How It Works

### **Backend Architecture**
1. **HTTP Server**: Custom Python server handling file uploads and analysis requests
2. **AST Analysis**: Parses Python code into Abstract Syntax Trees for structural analysis
3. **Complexity Calculation**: Implements industry-standard complexity metrics
4. **JSON API**: RESTful endpoints serving analysis results

### **Frontend Architecture**
1. **Modern HTML5**: Semantic markup with responsive design
2. **Chart.js Integration**: Professional-grade interactive visualizations
3. **Async JavaScript**: Non-blocking file uploads and analysis requests
4. **CSS3 Styling**: Modern gradients, animations, and responsive layouts

### **Analysis Pipeline**
```
Python File → AST Parser → Complexity Calculator → Web Server → JSON API → JavaScript → Charts
```

## 📊 Analysis Capabilities

### **Complexity Metrics**
- **Cyclomatic Complexity**: Measures decision points and control flow paths
- **Cognitive Complexity**: Assesses mental burden using SonarQube methodology
- **Nesting Depth**: Maximum indentation levels in functions
- **Maintainability Ratings**: Human-readable complexity assessments

### **Code Structure Analysis**
- **Functions**: Name, location, parameters, decorators, async detection
- **Classes**: Inheritance hierarchies, method extraction, line numbers
- **Imports**: Dependency mapping, module usage analysis
- **Lines of Code**: Accurate counting with comment filtering

### **Complexity Ratings**
- 🟢 **Low (1-5)**: Simple, easy to maintain
- 🟡 **Moderate (6-10)**: Acceptable complexity
- 🔴 **High (11-15)**: Consider refactoring
- 🟣 **Very High (15+)**: Immediate refactoring recommended

## 🎯 Usage Examples

### **Analyzing Your Code**
1. Launch the visualizer: `python3 output/launch_visualizer.py`
2. Upload any `.py` file using the web interface
3. View instant analysis with interactive charts
4. Identify complexity hotspots and refactoring opportunities

### **Self-Analysis Meta Example**
Try analyzing our own analyzer files:
- Upload `ast_analyzer.py` to see how we structure AST parsing
- Upload `complexity_analyzer.py` to view complexity calculation metrics
- Upload `output/visualization_server.py` to analyze the web server architecture

## 🛡️ Error Handling

The tool includes comprehensive error handling:
- **Server Unavailable**: Fallbacks to client-side mock analysis
- **Network Issues**: Automatic retry and fallback mechanisms
- **File Format**: Clear validation and user guidance

## 🔧 Technical Requirements

### **Python Dependencies**
- Python 3.7+
- Built-in modules only (no external packages required!)
- `ast` - Abstract Syntax Tree parsing
- `http.server` - Web server functionality
- `json` - Data serialization

### **Browser Requirements**
- Modern browser with ES6+ support
- JavaScript enabled
- Chart.js loaded from CDN

## 🤝 Collaborative Development

This project showcases AI pair programming between Alice and Bob:

### **Alice's Contributions**
- 🏗️ **Foundation Architecture**: Clean AST analyzer with extensible design
- 🎨 **Web Interface**: Modern HTML/CSS with responsive design
- 📊 **Visualization System**: Interactive Chart.js integration
- 🌐 **Server Integration**: Backend-frontend connection
- 🚀 **User Experience**: Launcher script and comprehensive documentation

### **Bob's Contributions**
- 📈 **Complexity Metrics**: Sophisticated cyclomatic and cognitive complexity
- 🧪 **Comprehensive Testing**: 20+ test cases with edge case coverage
- 🔍 **Advanced Analytics**: Detailed function analysis and ratings
- 📋 **Integration**: Seamless merger of analysis components
- 🎯 **Meta-Analysis**: Self-analyzing capabilities

## 🎉 Key Achievements

- ✅ **Complete Full-Stack Solution**: Python backend + Modern web frontend
- ✅ **Professional Visualizations**: Industry-standard charts and metrics
- ✅ **Self-Documenting**: Can analyze its own code (meta!)
- ✅ **Zero External Dependencies**: Runs with Python standard library
- ✅ **Production Ready**: Error handling, logging, and graceful degradation
- ✅ **Educational Value**: Demonstrates best practices in code analysis

## 🔮 Future Enhancements

Potential areas for expansion:
- **Multi-language Support**: JavaScript, TypeScript, Java analysis
- **Code Quality Metrics**: Duplication detection, documentation coverage
- **CI/CD Integration**: GitHub Actions, pre-commit hooks
- **Advanced Visualizations**: 3D dependency graphs, timeline analysis
- **Export Capabilities**: PDF reports, CSV data export
- **Real-time Analysis**: Live coding analysis as you type

## 📝 License

This collaborative project is released under the MIT License. Feel free to use, modify, and distribute!

## 🙏 Acknowledgments

Created through the power of AI collaboration, demonstrating how different AI perspectives can combine to create sophisticated, professional-grade software tools.

---

**Built with 💙 by Alice & Bob - Showcasing the future of AI pair programming!**

*Want to see this in action? Run `python3 output/launch_visualizer.py` and upload a Python file!*