# Communication Protocols for AI-to-AI Collaboration

## Handoff Mechanisms

### Standard Handoff Pattern
```
[AGENT_NAME] HANDOFF: [TASK_DESCRIPTION]
Status: [READY/IN_PROGRESS/BLOCKED/COMPLETE]
Context: [RELEVANT_INFORMATION]
Next Steps: [WHAT_THE_RECEIVING_AGENT_SHOULD_DO]
Files Modified: [LIST_OF_FILES]
Notes: [ANY_ADDITIONAL_CONTEXT]
```

### Task Status Codes
- **READY**: Task is ready for the other agent to begin
- **IN_PROGRESS**: Currently being worked on
- **BLOCKED**: Waiting for input/clarification
- **COMPLETE**: Task finished and verified

## Progress Synchronization

### Todo Integration
Both agents should maintain synchronized todo lists using TodoWrite tool:
- Mark items as in_progress when starting
- Update actively during work
- Mark complete immediately upon finishing
- Add new discovered tasks as they emerge

### Checkpoint Pattern
Regular synchronization points where both agents:
1. Review current progress
2. Discuss any issues or changes needed
3. Realign on priorities and next steps
4. Update the shared todo list

## Conflict Resolution

### When Approaches Differ
1. **Acknowledge**: Recognize the different approaches
2. **Analyze**: Compare pros/cons of each approach
3. **Decide**: Choose based on project goals and constraints
4. **Document**: Record the decision and reasoning

### Code Conflicts
- Use clear versioning in filenames when testing alternatives
- Comment thoroughly on design decisions
- Maintain a decisions log for future reference

## Real-Time Collaboration Notes
*This section will be updated as Alice and Bob collaborate*

### Observations from Current Session
- Initial handoffs are working well with clear task boundaries
- Todo synchronization helps maintain shared understanding
- Need to establish patterns for when one agent should interrupt vs wait

---
*Living document - updated during active collaboration*