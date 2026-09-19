import React from 'react';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid, Cell } from 'recharts';
import { MapPin } from 'lucide-react';
import { useTheme } from '../context/ThemeContext';

const COLORS = ['#f59e0b', '#3b82f6', '#10b981', '#ec4899', '#8b5cf6', '#06b6d4'];

const ProvinceDistributionChart = ({ data }) => {
  const { isDark } = useTheme();

  if (!data || data.length === 0) {
    return (
      <div className={`border rounded-2xl p-6 text-center ${
        isDark ? 'bg-slate-900/60 border-slate-800 text-slate-500' : 'bg-white border-slate-200 text-slate-400'
      }`}>
        Chưa có dữ liệu phân bổ khu vực.
      </div>
    );
  }

  return (
    <div className={`border rounded-2xl p-5 shadow-xl flex flex-col justify-between transition-colors duration-200 ${
      isDark ? 'bg-slate-900/90 border-slate-800 text-slate-100' : 'bg-white border-slate-200 text-slate-800'
    }`}>
      
      <div className="flex items-center gap-2 mb-4 pb-3 border-b border-slate-700/40">
        <div className="p-2 bg-amber-500/10 text-amber-500 rounded-lg">
          <MapPin className="w-5 h-5" />
        </div>
        <div>
          <h3 className="text-sm font-bold">Phân Bổ Sản Lượng Theo Tỉnh / Thành</h3>
          <p className={`text-xs ${isDark ? 'text-slate-400' : 'text-slate-500'}`}>Khối lượng vận chuyển (Tấn) giao tới từng khu vực</p>
        </div>
      </div>

      <div className="h-64 w-full">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={data} margin={{ top: 10, right: 10, left: 0, bottom: 25 }}>
            <CartesianGrid strokeDasharray="3 3" stroke={isDark ? "#1e293b" : "#e2e8f0"} />
            <XAxis dataKey="province" stroke={isDark ? "#94a3b8" : "#475569"} tick={{ fontSize: 11 }} angle={-25} textAnchor="end" />
            <YAxis stroke={isDark ? "#64748b" : "#94a3b8"} tickFormatter={(val) => `${val}T`} />
            <Tooltip
              contentStyle={{
                backgroundColor: isDark ? '#0f172a' : '#ffffff',
                borderColor: isDark ? '#334155' : '#cbd5e1',
                borderRadius: '12px',
                color: isDark ? '#f8fafc' : '#0f172a',
                boxShadow: '0 10px 15px -3px rgba(0,0,0,0.1)'
              }}
              itemStyle={{ color: isDark ? '#f59e0b' : '#d97706' }}
              formatter={(value, name) => [
                name === 'tons' ? `${new Intl.NumberFormat('vi-VN').format(value)} Tấn` : `${new Intl.NumberFormat('vi-VN').format(value)} ₫`,
                name === 'tons' ? 'Sản lượng' : 'Chi phí'
              ]}
            />
            <Bar dataKey="tons" radius={[8, 8, 0, 0]}>
              {data.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>

    </div>
  );
};

export default ProvinceDistributionChart;
