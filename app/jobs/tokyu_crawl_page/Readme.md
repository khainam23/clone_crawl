# Tokyu Crawl Page Module

## 📋 Overview

This module handles crawling property listings from Tokyu real estate website. It extracts comprehensive property information including building details, unit specifications, rental costs, and amenities.

## 🏗️ Structure

```
tokyu_crawl_page/
├── index.py                      # Entry point for crawling
├── custom_extractor_factory.py  # Factory for creating extractors
├── property_data_extractor.py   # Main data extraction logic
├── image_extractor.py            # Image extraction
├── map_extractor.py              # Map/coordinates extraction
├── constants.py                  # Configuration constants
└── Readme.md                     # This file
```

## ✨ Optimized Features

### 1. **Helper Methods Pattern**
- `_find_dt_dd()`: Extract content from `<dt>label</dt><dd>content</dd>` pattern
- `_find_td()`: Extract content from table `<th>label</th>...<td>content</td>` pattern
- Eliminates repetitive HTML parsing code
- Centralized HTML cleaning and extraction

### 2. **Clear Processing Pipeline**
The extraction process follows a well-defined 13-step pipeline:

```
1. Clean HTML → Store in _html field
2. Extract Images
3. Extract Building Info (name, type, structure, address, year)
4. Extract Unit Info (unit_no, floor, size, direction)
5. Extract Rental Costs (monthly_rent, monthly_maintenance)
6. Extract Other Fees (cleaning fee, other expenses)
7. Extract Unit Description (pet info, remarks)
8. Extract Deposits & Fees (deposit, key money, renewal)
9. Extract Amenities (from 設備・条件 section)
10. Extract Pet Policy (from 敷金積増 section)
11. Set Default Amenities
12. Calculate Financial Info (guarantor, agency, insurance, discount)
13. Extract Map Coordinates
14. Cleanup Temporary Fields
```

### 3. **Enhanced Error Handling**
- HTTP timeout support (30 seconds)
- Per-page error handling in listing crawl
- Safe wrapper for each extraction step
- Graceful degradation on failures

### 4. **Improved Logging**
- Emoji indicators for better visibility (🚀, 📄, ✅, ⚠️, 🎉)
- Clear progress tracking
- Detailed extraction logs with values

## 📊 Data Extraction

### Building Information
- **building_name_ja**: Building name in Japanese (物件名)
- **building_type**: Type of building (種別)
- **structure**: Building structure (建物構造)
- **address**: Full address (所在地)
- **year**: Construction year (築年月)

### Unit Information
- **unit_no**: Room number (部屋番号)
- **floor_no**: Floor number (所在階)
- **floors**: Total floors (階建)
- **size**: Unit size in m² (専有面積)
- **direction**: Facing direction (方位)

### Rental Costs
- **monthly_rent**: Monthly rent (賃料)
- **monthly_maintenance**: Maintenance fee (管理費・共益費)
- **numeric_deposit**: Deposit amount (敷金)
- **numeric_security_deposit**: Security deposit (保証金)
- **numeric_key**: Key money (礼金)
- **numeric_deposit_amortization**: Deposit amortization (償却・敷引)
- **numeric_renewal**: Renewal fee (更新料)

### Additional Fees
- **other_initial_fees**: Cleaning fee (清掃費)
- **fire_insurance**: Fire insurance (保険料)
- **numeric_discount**: Free rent discount (フリーレント)
- **numeric_agency**: Agency fee (calculated as 1.1 × monthly_rent)
- **numeric_guarantor**: Guarantor fee (50% of total monthly)
- **numeric_guarantor_max**: Max guarantor fee (100% of total monthly)

### Other Information
- **property_description_ja**: Property description (ペット可区分 + 備考)
- **property_other_expenses_ja**: Other expenses description
- **available_from**: Move-in date (入居可能日)
- **pets**: Pet policy (Y/N)
- **amenities**: Various amenities flags

## 🚀 Usage

```python
from app.jobs.tokyu_crawl_page.index import crawl_multi

# Run the crawler
await crawl_multi()
```

## 🔧 Configuration

Edit `constants.py` to configure:
- `URL_MULTI`: Base URL for listing pages
- `ITEM_SELECTOR`: CSS selector for property items
- `NUM_PAGES`: Number of pages to crawl
- `BASE_URL`: Base URL for building full URLs
- `DEFAULT_AMENITIES`: Default amenity values

## 📝 Code Optimization Summary

### Before Optimization
- ❌ Repetitive HTML extraction code
- ❌ Scattered error handling
- ❌ Unclear processing order
- ❌ Basic logging
- ❌ No timeout handling

### After Optimization
- ✅ Helper methods for common patterns
- ✅ Centralized error handling with safe wrappers
- ✅ Well-documented processing pipeline
- ✅ Enhanced logging with emoji indicators
- ✅ Timeout and error recovery
- ✅ Cleaner, more maintainable code
- ✅ ~50+ lines of code eliminated

## 🎯 Key Improvements

1. **Code Reduction**: Eliminated ~50+ lines through helper methods
2. **Maintainability**: Easier to add/modify extraction logic
3. **Reliability**: Better error handling and recovery
4. **Readability**: Clear structure with inline documentation
5. **Performance**: Optimized HTML parsing with helper methods

## 🔍 Processing Flow

```
index.py
  └─> _fetch_page_urls()
       ├─> Fetch listing pages (1 to NUM_PAGES)
       ├─> Extract property URLs
       └─> Return list of URLs
  └─> crawl_pages()
       └─> For each URL:
            └─> custom_extractor_factory.setup_custom_extractor()
                 ├─> Pre-hook: _pass_html() - Clean HTML
                 └─> Post-hooks: 13 extraction steps
                      └─> Each wrapped with _create_safe_wrapper()
```

## 📌 Notes

- All extraction methods follow the pattern: `(data: Dict, html: str) -> Dict`
- Helper methods are prefixed with `_` to indicate private usage
- Processing order is critical (e.g., rental costs must be extracted before calculating deposits)
- Station extraction is currently commented out (optional feature)
- Temporary `_html` field is cleaned up at the end of processing

## 🐛 Debugging

To debug extraction issues:

1. Check the HTML structure matches the expected pattern
2. Verify the Japanese labels in `_find_dt_dd()` and `_find_td()` calls
3. Review logs for specific extraction step failures
4. Test individual extraction methods with sample HTML

## 🔄 Future Enhancements

- [ ] Add retry logic for failed extractions
- [ ] Implement extraction success rate tracking
- [ ] Create base extractor class for shared functionality
- [ ] Add unit tests for extraction methods
- [ ] Support for additional property types