import React from 'react';
import { Filter, RotateCcw, Calendar, Truck, MapPin, Package, RefreshCw, ToggleLeft, ToggleRight } from 'lucide-react';
import { useTheme } from '../context/ThemeContext';

const Sidebar = ({ filterOptions, filters, onChangeFilter, onResetFilters, isLoading }) => {
  const { isDark } = useTheme();

  const handleMultiSelect = (key, value) => {
    const current = filters[key] || [];
    let updated;
    if (current.includes(value)) {
      updated = current.filter(item => item !== value);
    } else {
      updated = [...current, value];
    }
    onChangeFilter(key, updated);
  };

  const handleToggleReturn = () => {
    onChangeFilter('exclude_return', !filters.exclude_return);
  };

  return (
    <aside className={`w-full lg:w-72 border-r p-4 flex flex-col gap-5 transition-colors duration-200 ${
      isDark ? 'bg-slate-900/80 border-slate-800 text-slate-200' : 'bg-white border-slate-200 text-slate-800'
    }`}>
      
      <div className={`flex items-center justify-between pb-3 border-b ${isDark ? 'border-slate-800' : 'border-slate-200'}`}>
        <div className="flex items-center gap-2 font-bold">
          <Filter className="w-4 h-4 text-blue-500" />
          <span>Bộ Lọc Dữ Liệu</span>
          {isLoading && <RefreshCw className="w-3.5 h-3.5 text-blue-500 animate-spin ml-1" />}
        </div>
        <button
          onClick={onResetFilters}
          className={`text-xs flex items-center gap-1 transition ${
            isDark ? 'text-slate-400 hover:text-blue-400' : 'text-slate-500 hover:text-blue-600'
          }`}
          title="Reset bộ lọc"
        >
          <RotateCcw className="w-3 h-3" />
          <span>Đặt lại</span>
        </button>
      </div>

      {/* Exclude Returns Toggle */}
      <div className={`p-3 rounded-xl border flex items-center justify-between ${
        isDark ? 'bg-slate-800/60 border-slate-700/50' : 'bg-slate-50 border-slate-200'
      }`}>
        <div>
          <p className="text-xs font-semibold">Bỏ hàng trả về (`is_return`)</p>
          <p className={`text-[10px] ${isDark ? 'text-slate-400' : 'text-slate-500'}`}>Ẩn dòng hàng trả về khỏi KPI sản lượng</p>
        </div>
        <button onClick={handleToggleReturn} className="text-blue-500">
          {filters.exclude_return ? <ToggleRight className="w-6 h-6" /> : <ToggleLeft className="w-6 h-6 opacity-50" />}
        </button>
      </div>

      {/* 1. Year Filter */}
      <div className="space-y-2">
        <label className={`text-xs font-bold uppercase tracking-wider flex items-center gap-1.5 ${
          isDark ? 'text-slate-400' : 'text-slate-500'
        }`}>
          <Calendar className="w-3.5 h-3.5 text-blue-500" />
          <span>Năm</span>
        </label>
        <div className="flex flex-wrap gap-1.5">
          {(filterOptions?.years || []).map(year => {
            const isSelected = (filters.years || []).includes(year);
            return (
              <button
                key={year}
                onClick={() => handleMultiSelect('years', year)}
                className={`px-3 py-1 text-xs font-semibold rounded-lg border transition ${
                  isSelected
                    ? 'bg-blue-600 text-white border-blue-500 shadow-sm'
                    : isDark
                    ? 'bg-slate-950/60 border-slate-800 text-slate-300 hover:bg-slate-800'
                    : 'bg-slate-100 border-slate-200 text-slate-700 hover:bg-slate-200'
                }`}
              >
                {year}
              </button>
            );
          })}
        </div>
      </div>

      {/* 2. Month Filter */}
      <div className="space-y-2">
        <label className={`text-xs font-bold uppercase tracking-wider flex items-center gap-1.5 ${
          isDark ? 'text-slate-400' : 'text-slate-500'
        }`}>
          <Calendar className="w-3.5 h-3.5 text-blue-500" />
          <span>Tháng</span>
        </label>
        <div className="grid grid-cols-4 gap-1">
          {(filterOptions?.months || []).map(month => {
            const isSelected = (filters.months || []).includes(month);
            return (
              <button
                key={month}
                onClick={() => handleMultiSelect('months', month)}
                className={`py-1 text-xs font-semibold rounded-lg border text-center transition ${
                  isSelected
                    ? 'bg-blue-600 text-white border-blue-500 shadow-sm'
                    : isDark
                    ? 'bg-slate-950/60 border-slate-800 text-slate-300 hover:bg-slate-800'
                    : 'bg-slate-100 border-slate-200 text-slate-700 hover:bg-slate-200'
                }`}
              >
                T{month}
              </button>
            );
          })}
        </div>
      </div>

      {/* 3. Carrier Filter */}
      <div className="space-y-2">
        <label className={`text-xs font-bold uppercase tracking-wider flex items-center gap-1.5 ${
          isDark ? 'text-slate-400' : 'text-slate-500'
        }`}>
          <Truck className="w-3.5 h-3.5 text-blue-500" />
          <span>Nhà Vận Chuyển ({filterOptions?.carriers?.length || 0})</span>
        </label>
        <div className={`max-h-40 overflow-y-auto p-1.5 rounded-xl border space-y-1 ${
          isDark ? 'bg-slate-950/40 border-slate-800' : 'bg-slate-50 border-slate-200'
        }`}>
          {(filterOptions?.carriers || []).map(carrier => {
            const isSelected = (filters.carrier || []).includes(carrier);
            return (
              <label
                key={carrier}
                className={`flex items-center gap-2 p-1.5 rounded-lg text-xs cursor-pointer transition ${
                  isSelected
                    ? isDark ? 'bg-blue-600/20 text-blue-300 font-medium' : 'bg-blue-100 text-blue-800 font-medium'
                    : isDark ? 'hover:bg-slate-800/60 text-slate-300' : 'hover:bg-slate-200/60 text-slate-700'
                }`}
              >
                <input
                  type="checkbox"
                  checked={isSelected}
                  onChange={() => handleMultiSelect('carrier', carrier)}
                  className="rounded border-slate-700 text-blue-600 focus:ring-0"
                />
                <span className="truncate">{carrier}</span>
              </label>
            );
          })}
        </div>
      </div>

      {/* 4. Province Filter */}
      <div className="space-y-2">
        <label className={`text-xs font-bold uppercase tracking-wider flex items-center gap-1.5 ${
          isDark ? 'text-slate-400' : 'text-slate-500'
        }`}>
          <MapPin className="w-3.5 h-3.5 text-blue-500" />
          <span>Tỉnh / Thành ({filterOptions?.provinces?.length || 0})</span>
        </label>
        <div className={`max-h-40 overflow-y-auto p-1.5 rounded-xl border space-y-1 ${
          isDark ? 'bg-slate-950/40 border-slate-800' : 'bg-slate-50 border-slate-200'
        }`}>
          {(filterOptions?.provinces || []).map(prov => {
            const isSelected = (filters.province || []).includes(prov);
            return (
              <label
                key={prov}
                className={`flex items-center gap-2 p-1.5 rounded-lg text-xs cursor-pointer transition ${
                  isSelected
                    ? isDark ? 'bg-blue-600/20 text-blue-300 font-medium' : 'bg-blue-100 text-blue-800 font-medium'
                    : isDark ? 'hover:bg-slate-800/60 text-slate-300' : 'hover:bg-slate-200/60 text-slate-700'
                }`}
              >
                <input
                  type="checkbox"
                  checked={isSelected}
                  onChange={() => handleMultiSelect('province', prov)}
                  className="rounded border-slate-700 text-blue-600 focus:ring-0"
                />
                <span className="truncate">{prov}</span>
              </label>
            );
          })}
        </div>
      </div>

      {/* 5. Delivery Type Filter */}
      <div className="space-y-2">
        <label className={`text-xs font-bold uppercase tracking-wider flex items-center gap-1.5 ${
          isDark ? 'text-slate-400' : 'text-slate-500'
        }`}>
          <Package className="w-3.5 h-3.5 text-blue-500" />
          <span>Loại hình giao hàng</span>
        </label>
        <div className={`max-h-32 overflow-y-auto p-1.5 rounded-xl border space-y-1 ${
          isDark ? 'bg-slate-950/40 border-slate-800' : 'bg-slate-50 border-slate-200'
        }`}>
          {(filterOptions?.delivery_types || []).map(dtype => {
            const isSelected = (filters.delivery_type || []).includes(dtype);
            return (
              <label
                key={dtype}
                className={`flex items-center gap-2 p-1.5 rounded-lg text-xs cursor-pointer transition ${
                  isSelected
                    ? isDark ? 'bg-blue-600/20 text-blue-300 font-medium' : 'bg-blue-100 text-blue-800 font-medium'
                    : isDark ? 'hover:bg-slate-800/60 text-slate-300' : 'hover:bg-slate-200/60 text-slate-700'
                }`}
              >
                <input
                  type="checkbox"
                  checked={isSelected}
                  onChange={() => handleMultiSelect('delivery_type', dtype)}
                  className="rounded border-slate-700 text-blue-600 focus:ring-0"
                />
                <span className="truncate">{dtype}</span>
              </label>
            );
          })}
        </div>
      </div>

    </aside>
  );
};

export default Sidebar;
