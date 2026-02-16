import React from 'react'
import { InventoryList } from './components/InventoryList'
import { useInventory } from './hooks/useInventory'
import { Package } from 'lucide-react'

function App() {
  const { items, loading, error, lastSync, refreshItems } = useInventory()

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-4xl mx-auto px-4 py-4">
          <div className="flex items-center space-x-3">
            <div className="p-2 bg-primary-600 rounded-lg">
              <Package className="h-6 w-6 text-white" />
            </div>
            <div>
              <h1 className="text-xl font-semibold text-gray-900">
                Inventory Manager
              </h1>
              <p className="text-sm text-gray-600">
                TallyPrime Clean Slate System
              </p>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-4xl mx-auto px-4 py-6">
        <InventoryList
          items={items}
          loading={loading}
          error={error}
          lastSync={lastSync}
          onRefresh={refreshItems}
        />
      </main>

      {/* Footer */}
      <footer className="mt-12 py-6 text-center text-sm text-gray-500">
        <p>
          Powered by TallyPrime Clean Slate System
        </p>
      </footer>
    </div>
  )
}

export default App
