import React, { useState } from 'react';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid, Cell } from 'recharts';
import { Award, MousePointerClick } from 'lucide-react';
import { useTheme } from '../context/ThemeContext';

const COLORS = ['#3b82f6', '#10b981', '#f59e0b', '#8b5cf6', '#ec4899', '#06b6d4', '#6366f1', '#14b8a6'];

const CarrierRankingChart = ({ data, onCarrierClick }) => {
  const { isDark } = useTheme();
  const [metric, setMetric] = useState('tons');

  if (!data || data.length === 0) {
    return (
      <div className={`border rounded-2xl p-6 text-center ${
        isDark ? 'bg-slate-900/60 border-slate-800 text-slate-500' : 'bg-white border-slate-200 text-slate-400'
      }`}>
        Chưa có dữ liệu xếp hạng nhà vận chuyển.
      </div>
    );
  }

  const sortedData = [...data].sort((a, b) => (b[metric] || 0) - (a[metric] || 0));

  const formatValue = (val, key) => {
    if (key === 'cost') return new Intl.NumberFormat('vi-VN').format(val) + ' ₫';
    if (key === 'avg_unit_price') return new Intl.NumberFormat('vi-VN').format(val) + ' ₫/tấn';
    if (key === 'tons') return new Intl.NumberFormat('vi-VN').format(val) + ' Tấn';
    return new Intl.NumberFormat('vi-VN').format(val) + ' Lô';
  };

  return (
    <div className={`border rounded-2xl p-5 shadow-xl flex flex-col justify-between transition-colors duration-200 ${
      isDark ? 'bg-slate-900/90 border-slate-800 text-slate-100' : 'bg-white border-slate-200 text-slate-800'
    }`}>
      
      {/* Card Header & Metric Tabs */}
      <div className="flex flex-wrap items-center justify-between gap-3 mb-4 pb-3 border-b border-slate-700/40">
        <div className="flex items-center gap-2">
          <div className="p-2 bg-amber-500/10 text-amber-500 rounded-lg">
            <Award className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-sm font-bold">Xếp Hạng Nhà Vận Chuyển</h3>
            <p className={`text-xs flex items-center gap-1 ${isDark ? 'text-slate-400' : 'text-slate-500'}`}>
              <MousePointerClick className="w-3 h-3" />
              Click vào NVC để xem chi tiết tuyến
            </p>
          </div>
        </div>

        <div className={`flex items-center p-1 rounded-xl border text-xs ${
          isDark ? 'bg-slate-950/60 border-slate-800' : 'bg-slate-100 border-slate-200'
        }`}>
          <button
            onClick={() => setMetric('tons')}
            className={`px-3 py-1.5 rounded-lg font-medium transition ${metric === 'tons' ? 'bg-blue-600 text-white shadow' : 'text-slate-500 hover:text-slate-700'}`}
          >
            Sản lượng (Tấn)
          </button>
          <button
            onClick={() => setMetric('cost')}
            className={`px-3 py-1.5 rounded-lg font-medium transition ${metric === 'cost' ? 'bg-emerald-600 text-white shadow' : 'text-slate-500 hover:text-slate-700'}`}
          >
            Chi phí (VNĐ)
          </button>
          <button
            onClick={() => setMetric('shipments')}
            className={`px-3 py-1.5 rounded-lg font-medium transition ${metric === 'shipments' ? 'bg-purple-600 text-white shadow' : 'text-slate-500 hover:text-slate-700'}`}
          >
            Số Lô (Shipment)
          </button>
          <button
            onClick={() => setMetric('avg_unit_price')}
            className={`px-3 py-1.5 rounded-lg font-medium transition ${metric === 'avg_unit_price' ? 'bg-indigo-600 text-white shadow' : 'text-slate-500 hover:text-slate-700'}`}
          >
            Đơn giá TB / Tấn
          </button>
        </div>
      </div>

      {/* Chart */}
      <div className="h-64 w-full">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={sortedData} layout="vertical" margin={{ top: 5, right: 30, left: 40, bottom: 5 }}>
            <CartesianGrid strokeDasharray="3 3" stroke={isDark ? "#1e293b" : "#e2e8f0"} horizontal={false} />
            <XAxis type="number" stroke={isDark ? "#64748b" : "#94a3b8"} tickFormatter={(val) => val >= 1e6 ? `${(val/1e6).toFixed(0)}M` : val} />
            <YAxis type="category" dataKey="carrier_name" stroke={isDark ? "#94a3b8" : "#475569"} tick={{ fontSize: 12 }} width={110} />
            <Tooltip
              contentStyle={{
                backgroundColor: isDark ? '#0f172a' : '#ffffff',
                borderColor: isDark ? '#334155' : '#cbd5e1',
                borderRadius: '12px',
                color: isDark ? '#f8fafc' : '#0f172a',
                boxShadow: '0 10px 15px -3px rgba(0,0,0,0.1)'
              }}
              itemStyle={{ color: isDark ? '#38bdf8' : '#0284c7' }}
              formatter={(value) => [formatValue(value, metric), 'Giá trị']}
            />
            <Bar
              dataKey={metric}
              radius={[0, 8, 8, 0]}
              cursor={onCarrierClick ? 'pointer' : 'default'}
              onClick={(data) => onCarrierClick && onCarrierClick(data.carrier_name)}
            >
              {sortedData.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Mini Data Summary Table */}
      <div className={`mt-4 pt-3 border-t overflow-x-auto ${isDark ? 'border-slate-800' : 'border-slate-200'}`}>
        <table className="w-full text-xs text-left">
          <thead className={`text-[11px] uppercase ${isDark ? 'text-slate-400 bg-slate-950/40' : 'text-slate-500 bg-slate-100'}`}>
            <tr>
              <th className="px-2 py-1.5 rounded-l">NVC</th>
              <th className="px-2 py-1.5">Sản lượng</th>
              <th className="px-2 py-1.5">Tổng chi phí</th>
              <th className="px-2 py-1.5">Số Lô</th>
              <th className="px-2 py-1.5 text-right rounded-r">Đơn giá TB/Tấn</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-700/30">
            {sortedData.map((row) => (
              <tr
                key={row.carrier_name}
                className={`transition ${isDark ? 'hover:bg-blue-600/10' : 'hover:bg-blue-50'} ${onCarrierClick ? 'cursor-pointer' : ''}`}
                onClick={() => onCarrierClick && onCarrierClick(row.carrier_name)}
                title={onCarrierClick ? `Xem chi tiết tuyến của ${row.carrier_name}` : ''}
              >
                <td className="px-2 py-1.5 font-semibold flex items-center gap-1.5">
                  {onCarrierClick && <MousePointerClick className="w-3 h-3 text-blue-400 flex-shrink-0" />}
                  {row.carrier_name}
                </td>
                <td className="px-2 py-1.5 text-blue-500 font-medium">{new Intl.NumberFormat('vi-VN').format(row.tons)} Tấn</td>
                <td className="px-2 py-1.5 text-emerald-500 font-medium">{new Intl.NumberFormat('vi-VN').format(row.cost)} ₫</td>
                <td className="px-2 py-1.5 text-purple-500 font-medium">{row.shipments} Lô</td>
                <td className="px-2 py-1.5 text-right text-indigo-500 font-mono font-medium">{new Intl.NumberFormat('vi-VN').format(row.avg_unit_price)} ₫</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

    </div>
  );
};

export default CarrierRankingChart;
