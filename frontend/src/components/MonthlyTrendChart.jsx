import React from 'react';
import { AreaChart, Area, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid, Legend } from 'recharts';
import { Calendar } from 'lucide-react';
import { useTheme } from '../context/ThemeContext';

const MonthlyTrendChart = ({ data }) => {
  const { isDark } = useTheme();

  if (!data || data.length === 0) {
    return (
      <div className={`border rounded-2xl p-6 text-center ${
        isDark ? 'bg-slate-900/60 border-slate-800 text-slate-500' : 'bg-white border-slate-200 text-slate-400'
      }`}>
        Chưa có dữ liệu xu hướng theo tháng.
      </div>
    );
  }

  return (
    <div className={`border rounded-2xl p-5 shadow-xl flex flex-col justify-between transition-colors duration-200 ${
      isDark ? 'bg-slate-900/90 border-slate-800 text-slate-100' : 'bg-white border-slate-200 text-slate-800'
    }`}>
      
      <div className="flex items-center gap-2 mb-4 pb-3 border-b border-slate-700/40">
        <div className="p-2 bg-blue-500/10 text-blue-500 rounded-lg">
          <Calendar className="w-5 h-5" />
        </div>
        <div>
          <h3 className="text-sm font-bold">Xu Hướng Sản Lượng Theo Thời Gian</h3>
          <p className={`text-xs ${isDark ? 'text-slate-400' : 'text-slate-500'}`}>Biến động số tấn và tổng chi phí vận chuyển theo tháng</p>
        </div>
      </div>

      <div className="h-64 w-full">
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={data} margin={{ top: 10, right: 20, left: 0, bottom: 5 }}>
            <defs>
              <linearGradient id="colorTons" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.8}/>
                <stop offset="95%" stopColor="#3b82f6" stopOpacity={0}/>
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke={isDark ? "#1e293b" : "#e2e8f0"} />
            <XAxis dataKey="month" stroke={isDark ? "#94a3b8" : "#475569"} tick={{ fontSize: 11 }} />
            <YAxis yAxisId="left" stroke="#3b82f6" tickFormatter={(val) => `${val}T`} />
            <YAxis yAxisId="right" orientation="right" stroke="#10b981" tickFormatter={(val) => val >= 1e6 ? `${(val/1e6).toFixed(0)}M` : val} />
            <Tooltip
              contentStyle={{
                backgroundColor: isDark ? '#0f172a' : '#ffffff',
                borderColor: isDark ? '#334155' : '#cbd5e1',
                borderRadius: '12px',
                color: isDark ? '#f8fafc' : '#0f172a',
                boxShadow: '0 10px 15px -3px rgba(0,0,0,0.1)'
              }}
              formatter={(value, name) => [
                name === 'tons' ? `${new Intl.NumberFormat('vi-VN').format(value)} Tấn` : `${new Intl.NumberFormat('vi-VN').format(value)} ₫`,
                name === 'tons' ? 'Sản lượng (Tấn)' : 'Chi phí (VNĐ)'
              ]}
            />
            <Legend />
            <Area yAxisId="left" type="monotone" dataKey="tons" name="Sản lượng (Tấn)" stroke="#3b82f6" fillOpacity={1} fill="url(#colorTons)" />
          </AreaChart>
        </ResponsiveContainer>
      </div>

    </div>
  );
};

export default MonthlyTrendChart;
