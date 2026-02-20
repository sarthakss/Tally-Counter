import { useState, useEffect, useCallback, useMemo } from 'react'

interface UseVirtualizedListProps<T> {
  items: T[]
  itemHeight: number
  containerHeight: number
  overscan?: number
}

export function useVirtualizedList<T>({
  items,
  itemHeight,
  containerHeight,
  overscan = 5
}: UseVirtualizedListProps<T>) {
  const [scrollTop, setScrollTop] = useState(0)

  const visibleCount = Math.ceil(containerHeight / itemHeight)
  const startIndex = Math.max(0, Math.floor(scrollTop / itemHeight) - overscan)
  const endIndex = Math.min(items.length - 1, startIndex + visibleCount + overscan * 2)

  const visibleItems = useMemo(() => {
    return items.slice(startIndex, endIndex + 1).map((item, index) => ({
      item,
      index: startIndex + index
    }))
  }, [items, startIndex, endIndex])

  const totalHeight = items.length * itemHeight

  const handleScroll = useCallback((e: React.UIEvent<HTMLDivElement>) => {
    setScrollTop(e.currentTarget.scrollTop)
  }, [])

  return {
    visibleItems,
    totalHeight,
    startIndex,
    handleScroll,
    offsetY: startIndex * itemHeight
  }
}
