import React from 'react';
import { Weight, DollarSign, Truck, Package, MapPin, TrendingUp, RotateCcw } from 'lucide-react';
import { useTheme } from '../context/ThemeContext';

const KPICards = ({ kpis }) => {
  const { isDark } = useTheme();

  if (!kpis) return null;

  const formatNumber = (val) => new Intl.NumberFormat('vi-VN').format(val || 0);
  const formatCurrency = (val) => {
    if (!val) return '0 ₫';
    if (val >= 1e9) return (val / 1e9).toFixed(2) + ' Tỷ ₫';
    if (val >= 1e6) return (val / 1e6).toFixed(1) + ' Tr ₫';
    return formatNumber(val) + ' ₫';
  };

  const cards = [
    {
      title: 'Tổng sản lượng',
      value: `${formatNumber(kpis.total_tons)} Tấn`,
      sub: `${formatNumber(kpis.total_records)} dòng dữ liệu`,
      icon: Weight,
      textColor: 'text-blue-500',
      bgColor: 'bg-blue-500/10 border-blue-500/20'
    },
    {
      title: 'Tổng chi phí vận chuyển',
      value: formatCurrency(kpis.total_cost),
      sub: 'Cước chính + Phụ phí',
      icon: DollarSign,
      textColor: 'text-emerald-500',
      bgColor: 'bg-emerald-500/10 border-emerald-500/20'
    },
    {
      title: 'Số nhà vận chuyển',
      value: `${kpis.carrier_count} NVC`,
      sub: 'Đang hoạt động trong kỳ',
      icon: Truck,
      textColor: 'text-amber-500',
      bgColor: 'bg-amber-500/10 border-amber-500/20'
    },
    {
      title: 'Tổng số Lô hàng',
      value: `${formatNumber(kpis.shipment_count)} Shipment`,
      sub: 'Số chuyến xe / lô SAP',
      icon: Package,
      textColor: 'text-purple-500',
      bgColor: 'bg-purple-500/10 border-purple-500/20'
    },
    {
      title: 'Số Tỉnh / Thành phủ sóng',
      value: `${kpis.province_count} Khu vực`,
      sub: 'Tỉnh thành có giao hàng',
      icon: MapPin,
      textColor: 'text-cyan-500',
      bgColor: 'bg-cyan-500/10 border-cyan-500/20'
    },
    {
      title: 'Đơn giá cước TB / Tấn',
      value: `${formatNumber(kpis.avg_unit_price)} ₫/tấn`,
      sub: 'Trung bình toàn hệ thống',
      icon: TrendingUp,
      textColor: 'text-indigo-500',
      bgColor: 'bg-indigo-500/10 border-indigo-500/20'
    },
    {
      title: 'Tỷ lệ hàng Trả về',
      value: `${kpis.return_rate}%`,
      sub: 'Số chuyến bị hoãn / trả',
      icon: RotateCcw,
      textColor: 'text-rose-500',
      bgColor: 'bg-rose-500/10 border-rose-500/20'
    }
  ];

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 xl:grid-cols-7 gap-4">
      {cards.map((c, idx) => {
        const IconComponent = c.icon;
        return (
          <div
            key={idx}
            className={`p-4 rounded-2xl border transition-all duration-200 shadow-md ${
              isDark ? 'bg-slate-900/90 border-slate-800 text-slate-100' : 'bg-white border-slate-200 text-slate-800'
            }`}
          >
            <div className="flex items-center justify-between mb-3">
              <span className={`text-[11px] font-bold uppercase tracking-wider ${isDark ? 'text-slate-400' : 'text-slate-500'}`}>
                {c.title}
              </span>
              <div className={`p-2 rounded-xl border ${c.bgColor} ${c.textColor}`}>
                <IconComponent className="w-4 h-4" />
              </div>
            </div>

            <div className="text-lg font-extrabold tracking-tight truncate">
              {c.value}
            </div>

            <p className={`text-[11px] mt-1 truncate ${isDark ? 'text-slate-400' : 'text-slate-500'}`}>
              {c.sub}
            </p>
          </div>
        );
      })}
    </div>
  );
};

export default KPICards;
