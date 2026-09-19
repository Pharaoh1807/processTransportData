import React from 'react';
import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer, Legend } from 'recharts';
import { DollarSign } from 'lucide-react';
import { useTheme } from '../context/ThemeContext';

const COLORS = ['#10b981', '#3b82f6', '#f59e0b', '#8b5cf6', '#ec4899', '#06b6d4', '#6366f1', '#14b8a6'];

const CostBreakdownChart = ({ data }) => {
  const { isDark } = useTheme();

  if (!data || data.length === 0) {
    return (
      <div className={`border rounded-2xl p-6 text-center ${
        isDark ? 'bg-slate-900/60 border-slate-800 text-slate-500' : 'bg-white border-slate-200 text-slate-400'
      }`}>
        Chưa có dữ liệu cơ cấu cước phí.
      </div>
    );
  }

  const totalCostSum = data.reduce((acc, curr) => acc + (curr.amount || 0), 0);

  return (
    <div className={`border rounded-2xl p-5 shadow-xl flex flex-col justify-between transition-colors duration-200 ${
      isDark ? 'bg-slate-900/90 border-slate-800 text-slate-100' : 'bg-white border-slate-200 text-slate-800'
    }`}>
      
      <div className="flex items-center gap-2 mb-4 pb-3 border-b border-slate-700/40">
        <div className="p-2 bg-emerald-500/10 text-emerald-500 rounded-lg">
          <DollarSign className="w-5 h-5" />
        </div>
        <div>
          <h3 className="text-sm font-bold">Cơ Cấu Các Loại Phí Vận Chuyển</h3>
          <p className={`text-xs ${isDark ? 'text-slate-400' : 'text-slate-500'}`}>Tỷ trọng các mã phí SAP (ZF, ZSC, ZT)</p>
        </div>
      </div>

      <div className="h-64 w-full flex items-center justify-center">
        <ResponsiveContainer width="100%" height="100%">
          <PieChart>
            <Pie
              data={data}
              cx="50%"
              cy="50%"
              innerRadius={55}
              outerRadius={85}
              paddingAngle={4}
              dataKey="amount"
              nameKey="name"
            >
              {data.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
              ))}
            </Pie>
            <Tooltip
              contentStyle={{
                backgroundColor: isDark ? '#0f172a' : '#ffffff',
                borderColor: isDark ? '#334155' : '#cbd5e1',
                borderRadius: '12px',
                color: isDark ? '#f8fafc' : '#0f172a',
                boxShadow: '0 10px 15px -3px rgba(0,0,0,0.1)'
              }}
              formatter={(value) => [
                `${new Intl.NumberFormat('vi-VN').format(value)} ₫ (${totalCostSum > 0 ? ((value/totalCostSum)*100).toFixed(1) : 0}%)`,
                'Chi phí'
              ]}
            />
            <Legend layout="horizontal" verticalAlign="bottom" align="center" wrapperStyle={{ fontSize: '11px', paddingTop: '10px' }} />
          </PieChart>
        </ResponsiveContainer>
      </div>

    </div>
  );
};

export default CostBreakdownChart;
