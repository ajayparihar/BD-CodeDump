# Drag and Drop Card Positioning - Compy 2.0

## Overview
Compy 2.0 implements a sophisticated drag and drop system for reordering snippet cards using SortableJS library. This system provides smooth, accessible, and responsive card repositioning with comprehensive visual feedback and state management integration.

## Architecture

### Core Components

#### 1. Drag Drop Manager (`/js/components/dragDrop.js`)
The main component responsible for managing drag and drop functionality:

```javascript
// Factory function to create drag and drop manager
export const createDragDropManager = (options = {}) => {
  // Handles SortableJS initialization, event handling, and state sync
}

// Convenience wrapper for app integration
export const createCardDragDropManager = (container, options = {}) => {
  // Pre-configured for snippet cards with state management
}
```

#### 2. State Management Integration (`/js/state.js`)
Handles persistent storage of card positions:

```javascript
export const reorderItems = (orderedIds) => {
  // Updates position values based on new order
  // Maintains sort order and triggers persistence
}
```

#### 3. App Integration (`/js/app.js`)
Main application coordinates drag and drop with other systems:

```javascript
initDragAndDrop() {
  // Creates drag manager instance
  // Sets up accessibility features
  // Handles reduced motion preferences
}
```

## Features

### 🖱️ Multi-Input Support
- **Mouse**: Full drag and drop with visual feedback
- **Touch**: Mobile-optimized with enhanced touch targets
- **Keyboard**: Arrow keys with Ctrl/Cmd for reordering

### 🎨 Visual Feedback System

#### Drag Handle
- **Location**: Bottom-left corner of each card
- **Appearance**: Grip dots icon with hover effects
- **Visibility**: Shows on card hover/focus/selection
- **States**: Normal, hover, active (grabbing), disabled

#### Drag States
1. **Normal**: Card ready for dragging
2. **Chosen**: Card being actively dragged
3. **Ghost**: Placeholder where card was
4. **Drag**: Visual appearance of dragging card
5. **Drop Indicators**: Lines showing drop zones

### ♿ Accessibility Features
- **ARIA attributes**: `aria-grabbed`, `aria-label`
- **Keyboard navigation**: Full reordering without mouse
- **Screen reader announcements**: Position changes announced
- **High contrast support**: Enhanced visibility
- **Reduced motion support**: Respects user preferences

## Implementation Details

### SortableJS Configuration

```javascript
sortableInstance = new Sortable(container, {
  // Animation and timing
  animation: prefersReducedMotion ? 0 : 150,
  easing: 'cubic-bezier(0.2, 0.8, 0.2, 1)',
  
  // Drag configuration
  draggable: '.card',
  handle: '.drag-handle',
  swapThreshold: 0.45,
  invertSwap: false,
  
  // Visual feedback classes
  ghostClass: 'card-ghost',
  chosenClass: 'card-chosen',
  dragClass: 'card-drag',
  
  // Touch support
  touchStartThreshold: 3,
  delay: 120,
  delayOnTouchOnly: true,
  
  // Scrolling behavior
  scroll: true,
  scrollSensitivity: 24,
  scrollSpeed: 10
});
```

### Event Handling Flow

#### 1. Drag Start
```javascript
onStart: (event) => {
  // Store dragging element
  dragStartElement = event.item;
  
  // Add container visual state
  container.classList.add('cards-dragging');
  
  // Disable text selection
  document.body.style.userSelect = 'none';
  
  // Set ARIA attributes
  event.item.setAttribute('aria-grabbed', 'true');
  
  // Call custom callback
  if (onStart) onStart(event);
}
```

#### 2. Drag Movement
```javascript
onMove: (evt) => {
  // Clear previous indicators
  clearIndicators();
  
  // Show drop indicator line
  const related = evt.related;
  if (related && related.classList.contains('card')) {
    related.setAttribute('data-drop-indicator', 
      evt.willInsertAfter ? 'after' : 'before');
  }
  
  return true; // Allow default behavior
}
```

#### 3. Drag End
```javascript
onEnd: (event) => {
  // Clean up visual states
  container.classList.remove('cards-dragging');
  document.body.style.userSelect = '';
  clearIndicators();
  
  // Handle reordering if position changed
  if (event.oldIndex !== event.newIndex) {
    handleReorder(event);
    
    // Announce to screen readers
    const message = `Moved ${title} to position ${newIndex + 1} of ${total}`;
    announceToScreenReader(message);
  }
  
  // Reset ARIA attributes
  event.item.setAttribute('aria-grabbed', 'false');
}
```

### State Management Integration

#### Position Update System
```javascript
const handleReorder = (event) => {
  // Extract new order from DOM
  const cardElements = container.querySelectorAll('[data-card-id]');
  const orderedIds = Array.from(cardElements).map(el => el.dataset.cardId);
  
  // Update state via reorderItems function
  onReorder(orderedIds); // Calls reorderItems(orderedIds)
};

export const reorderItems = (orderedIds) => {
  // Create position mapping
  const positionMap = new Map();
  orderedIds.forEach((id, index) => {
    positionMap.set(id, index);
  });
  
  // Update items with new positions
  const updatedItems = state.items.map(item => ({
    ...item,
    position: positionMap.has(item.id) ? positionMap.get(item.id) : item.position
  })).sort((a, b) => a.position - b.position);
  
  // Update state and persist
  state = { ...state, items: updatedItems };
  saveState();
};
```

### Keyboard Navigation

#### Supported Keys
- **Ctrl/Cmd + ↑**: Move card up one position
- **Ctrl/Cmd + ↓**: Move card down one position
- **Ctrl/Cmd + Home**: Move card to top
- **Ctrl/Cmd + End**: Move card to bottom
- **Space/Enter**: Copy card content (when not grabbed)

#### Implementation
```javascript
card.addEventListener('keydown', (e) => {
  const cardIndex = parseInt(card.dataset.cardIndex);
  
  switch (e.key) {
    case 'ArrowUp':
      if (e.ctrlKey || e.metaKey) {
        e.preventDefault();
        if (!this.isReorderDisabled()) {
          this.moveCardUp(cardIndex);
        }
      }
      break;
    // ... other cases
  }
});
```

## CSS Styling System

### Drag Handle Styling
```css
.card .drag-handle {
  position: absolute !important;
  left: 8px !important;
  bottom: 8px !important;
  width: 36px !important;
  height: 36px !important;
  display: none; /* shown on hover/focus */
  cursor: grab !important;
  background: transparent !important;
  border: 1px solid var(--border-interactive) !important;
  border-radius: var(--radius-sm) !important;
}

/* Show on interaction */
.card:hover .drag-handle,
.card:focus-within .drag-handle,
.card.selected .drag-handle {
  display: flex !important;
}
```

### Drag State Classes
```css
/* Active dragging */
.card.card-chosen {
  cursor: grabbing;
  z-index: 1000;
  box-shadow: 0 0 0 2px var(--primary);
}

/* Ghost placeholder */
.card.card-ghost {
  opacity: 0.2;
  background: var(--surface);
  border: none;
}

/* Drop indicators */
.card[data-drop-indicator="before"]::before {
  content: '';
  position: absolute;
  left: 8px;
  right: 8px;
  top: -1px;
  height: 2px;
  background: var(--primary);
}
```

### Responsive Design
```css
/* Mobile touch improvements */
@media (hover: none) and (pointer: coarse) {
  /* Always show drag handle on touch */
  .card .drag-handle {
    display: flex !important;
  }
  
  /* Enhanced touch feedback */
  .card.card-chosen {
    transform: scale(1.05) rotate(1deg);
  }
}

/* Reduced motion support */
@media (prefers-reduced-motion: reduce) {
  .card.card-drag,
  .card.card-chosen {
    transform: none;
    transition: none;
  }
}
```

## Disable/Enable Logic

### When Dragging is Disabled
Drag and drop is automatically disabled when:
1. **Search is active**: Prevents reordering filtered results
2. **Filters are applied**: Maintains filter integrity
3. **Only one card visible**: No reordering possible
4. **Card is expanded**: Prevents accidental drags

### Implementation
```javascript
isReorderDisabled() {
  const state = getState();
  const hasSearch = !!(state.search && state.search.trim());
  const hasFilters = Array.isArray(state.filterTags) && state.filterTags.length > 0;
  return hasSearch || hasFilters || this.cardElements.length <= 1;
}

// Visual feedback for disabled state
updateDragHandleTooltips(isDisabled) {
  const handles = document.querySelectorAll('.drag-handle');
  handles.forEach(handle => {
    handle.setAttribute('title', 
      isDisabled ? 'Clear search and filters to reorder' : 'Drag to reorder'
    );
    if (isDisabled) {
      handle.setAttribute('aria-disabled', 'true');
    } else {
      handle.removeAttribute('aria-disabled');
    }
  });
}
```

## Error Handling

### Drag Operation Recovery
```javascript
const handleReorder = (event) => {
  try {
    // Extract new order and update state
    const orderedIds = getOrderedIds();
    onReorder(orderedIds);
  } catch (error) {
    Logger.error('Reorder failed:', error);
    
    // Revert DOM changes
    if (event && event.item && event.from) {
      try {
        if (event.oldIndex < event.from.children.length) {
          event.from.insertBefore(event.item, event.from.children[event.oldIndex]);
        } else {
          event.from.appendChild(event.item);
        }
      } catch (revertError) {
        Logger.error('Failed to revert drag operation:', revertError);
      }
    }
  }
};
```

### Initialization Safety
```javascript
const initializeSortable = () => {
  if (!window.Sortable) {
    Logger.error('SortableJS not loaded');
    throw new Error('SortableJS not available');
  }
  
  // Validate container
  if (!container || !(container instanceof HTMLElement)) {
    throw new Error('Invalid container element');
  }
  
  // Initialize with error handling
  try {
    sortableInstance = new Sortable(container, config);
    isInitialized = true;
  } catch (error) {
    Logger.error('Failed to initialize SortableJS:', error);
    throw error;
  }
};
```

## Performance Optimizations

### Efficient Event Handling
- **Debounced updates**: Prevents excessive state updates
- **Minimal DOM queries**: Cached selectors where possible
- **Event delegation**: Single listeners handle multiple cards
- **RequestAnimationFrame**: Smooth visual updates

### Memory Management
- **Cleanup on destroy**: Removes event listeners and references
- **Weak references**: Prevents memory leaks
- **Efficient filtering**: Optimized position updates

### Animation Performance
- **CSS transforms**: Hardware-accelerated animations
- **Reduced motion respect**: Disables animations when requested
- **Optimized transitions**: Minimal reflow/repaint operations

## Browser Compatibility

### Supported Browsers
- **Chrome 60+**: Full support
- **Firefox 60+**: Full support  
- **Safari 12+**: Full support
- **Edge 79+**: Full support

### Fallback Behavior
- **No SortableJS**: Keyboard-only reordering available
- **No touch support**: Mouse-only interaction
- **Old browsers**: Graceful degradation to basic functionality

## Testing Considerations

### Test Cases
1. **Drag between positions**: Verify correct reordering
2. **Touch gestures**: Ensure mobile functionality
3. **Keyboard navigation**: Test all keyboard shortcuts
4. **Error recovery**: Verify revert on failures
5. **State persistence**: Check position saving
6. **Accessibility**: Screen reader announcements
7. **Performance**: Large list handling

### Edge Cases
- Empty card lists
- Single card scenarios
- Network interruption during save
- Rapid successive drags
- Mixed input methods (touch + mouse)

## Future Enhancements

### Potential Features
1. **Multi-select dragging**: Move multiple cards at once
2. **Folder system**: Drag cards into categories
3. **Undo/Redo**: Revert reordering operations
4. **Drag previews**: Enhanced visual feedback
5. **Batch operations**: Keyboard-based bulk reordering

### Performance Improvements
1. **Virtual scrolling**: Handle thousands of cards
2. **Web Workers**: Background position calculations
3. **IndexedDB**: Faster persistence for large datasets
4. **Gesture recognition**: Advanced touch interactions

## Conclusion

The drag and drop system in Compy 2.0 provides a comprehensive, accessible, and performant solution for card reordering. It integrates seamlessly with the application's state management, respects user preferences, and provides excellent visual feedback across all interaction modes.

The system is designed to be:
- **Accessible**: Full keyboard navigation and screen reader support
- **Responsive**: Optimized for both desktop and mobile
- **Performant**: Smooth animations with minimal impact
- **Reliable**: Comprehensive error handling and recovery
- **Maintainable**: Clean, modular code with clear separation of concerns

This implementation serves as a robust foundation for snippet management and can be extended to support additional features as the application grows.