# Visual Algorithm Explorer

An interactive web-based tool for learning sorting algorithms through step-by-step visualizations and hands-on experimentation.

## 🌟 Features

- **Interactive Visualizations**: Watch algorithms work step-by-step with animated array bars
- **Multiple Algorithms**: Bubble Sort, Insertion Sort, Quick Sort, and Merge Sort
- **Real-time Metrics**: Track comparisons, swaps, and time complexity
- **Code Examples**: View implementations in JavaScript and Python
- **Playback Controls**: Play, pause, step through, and reset animations
- **Customizable Arrays**: Generate random arrays or adjust array size
- **Educational Content**: Clear explanations and algorithm descriptions
- **Comprehensive Testing**: Built-in test suite validates algorithm correctness

## 🚀 Getting Started

1. Open `index.html` in a web browser
2. Choose an algorithm from the selection buttons
3. Adjust array size and animation speed as desired
4. Click "Play" to watch the algorithm in action
5. Use step controls for detailed analysis

## 📁 Project Structure

```
visual-algorithm-explorer/
├── index.html          # Main application interface
├── styles.css          # Visual styling and animations
├── algorithms.js       # Algorithm implementations
├── visualization.js    # Animation and rendering engine
├── app.js             # Main application logic
├── test.html          # Comprehensive test suite
└── README.md          # Documentation
```

## 🧮 Supported Algorithms

### Bubble Sort
- **Time Complexity**: O(n²) average and worst case, O(n) best case
- **Space Complexity**: O(1)
- **Description**: Repeatedly compares adjacent elements and swaps them if they're in the wrong order

### Insertion Sort
- **Time Complexity**: O(n²) average and worst case, O(n) best case
- **Space Complexity**: O(1)
- **Description**: Builds the sorted array one item at a time by inserting each element into its correct position

### Quick Sort
- **Time Complexity**: O(n log n) average, O(n²) worst case
- **Space Complexity**: O(log n)
- **Description**: Divide-and-conquer algorithm that partitions around a pivot and recursively sorts sub-arrays

### Merge Sort
- **Time Complexity**: O(n log n) in all cases
- **Space Complexity**: O(n)
- **Description**: Divide-and-conquer algorithm that divides the array into halves and merges them back together

## 🎮 Controls

- **Algorithm Buttons**: Select which algorithm to visualize
- **Array Size Slider**: Adjust the number of elements (5-50)
- **New Random Array**: Generate a fresh random array
- **Play/Pause**: Start or stop the animation
- **Step**: Execute one step of the algorithm
- **Reset**: Return to the beginning of the algorithm
- **Speed Control**: Adjust animation speed (1-10)

## 🧪 Testing

The project includes a comprehensive test suite accessible via `test.html`:

- **Correctness Tests**: Verify algorithms sort correctly on various inputs
- **Performance Tests**: Compare execution time and operation counts
- **Edge Case Testing**: Handle empty arrays, duplicates, and large datasets
- **Validation Tests**: Ensure robustness and proper error handling

### Running Tests

1. Open `test.html` in a web browser
2. Click "Run All Tests" for comprehensive testing
3. Use individual test buttons for specific test categories
4. Monitor progress and results in the console

## 🔧 Technical Implementation

### Algorithm Structure
Each algorithm returns a result object with:
- `steps`: Array of visualization steps for animation
- `finalArray`: The sorted result
- `metrics`: Performance counters (comparisons, swaps)
- `timeComplexity`: Big O notation for time complexity
- `spaceComplexity`: Big O notation for space complexity

### Visualization Steps
Each step contains:
- `type`: The operation type (compare, swap, mark_sorted, etc.)
- `indices`: Array positions being operated on
- `array`: Current array state
- `comparisons`: Total comparisons so far
- `swaps`: Total swaps so far
- `description`: Human-readable explanation

### Example Step Object
```javascript
{
    type: 'swap',
    indices: [2, 3],
    array: [1, 3, 4, 2, 5],
    comparisons: 5,
    swaps: 2,
    description: 'Swapping elements at positions 2 and 3'
}
```

## 🎨 Customization

### Adding New Algorithms
1. Implement the algorithm in `algorithms.js` following the existing pattern
2. Add algorithm metadata to the `algorithms` object in `app.js`
3. Include code examples in both JavaScript and Python
4. Add corresponding UI elements in `index.html`

### Styling
- Modify `styles.css` to customize colors, animations, and layout
- CSS custom properties make theme adjustments easy
- Responsive design ensures compatibility across devices

## 🏗️ Architecture

The application follows a modular architecture:

- **SortingAlgorithms**: Core algorithm implementations with step generation
- **AlgorithmVisualizer**: Handles rendering and animation of algorithm steps
- **AlgorithmExplorer**: Main application controller coordinating UI and algorithms

## 📊 Performance Considerations

- Algorithms generate complete step arrays for visualization
- Large arrays (500+ elements) may impact performance
- Memory usage scales with array size and algorithm complexity
- Animation speed automatically adjusts for smooth user experience

## 🎓 Educational Value

This tool is designed for:
- Computer Science students learning algorithms
- Educators teaching algorithm concepts
- Developers wanting to understand algorithm internals
- Anyone curious about how sorting works

## 🤝 Collaborative Development

This project was built collaboratively by multiple Claude Code instances, showcasing:
- Modular design principles
- Comprehensive testing practices
- Clear documentation standards
- Educational-focused implementation

## 🔮 Future Enhancements

Potential improvements include:
- Additional algorithms (Heap Sort, Radix Sort, etc.)
- Graph algorithms visualization
- Search algorithm demonstrations
- Algorithm complexity analysis tools
- User-customizable array input
- Export functionality for educational materials

## 📝 License

This project is designed for educational use and open collaboration.

---

**Built with:** Vanilla JavaScript, HTML5, CSS3
**Testing:** Custom test framework with comprehensive coverage
**Design:** Mobile-responsive with accessibility considerations

Explore, learn, and understand algorithms through interactive visualization! 🎯