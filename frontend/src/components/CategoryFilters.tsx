import { Category } from '../types'

const categories: Category[] = ['All', 'Game Outcome', 'Passing Yards', 'Rushing Yards', 'Receiving Yards', 'TDs']

interface CategoryFiltersProps {
  selected: Category
  onChange: (category: Category) => void
}

function CategoryFilters({ selected, onChange }: CategoryFiltersProps) {
  return (
    <div className="category-filters" aria-label="Prop categories">
      {categories.map((category) => (
        <button
          className={`filter-button${selected === category ? ' selected' : ''}`}
          type="button"
          aria-pressed={selected === category}
          onClick={() => onChange(category)}
          key={category}
        >
          {category}
        </button>
      ))}
    </div>
  )
}

export default CategoryFilters
