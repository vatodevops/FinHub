'use client';

import { useEffect, useState } from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell, LineChart, Line, Legend } from 'recharts';
import { PageSection } from '@/components/PageSection';
import { Topbar } from '@/components/Topbar';
import { api, type MonthlySummary, type CategoryBreakdown, type NetWorthPoint } from '@/lib/api';

function money(value: string | number) {
  const n = Number(value || 0);
  return new Intl.NumberFormat('es-ES', { style: 'currency', currency: 'EUR' }).format(n);
}

const CHART_COLORS = ['#56d364', '#6ea8fe', '#ff9f43', '#ef4444', '#a78bfa', '#ec4899', '#14b8a6', '#f59e0b', '#8b5cf6', '#22d3ee', '#f97316', '#64748b'];

export default function ReportsPage() {
  const [monthly, setMonthly] = useState<MonthlySummary[]>([]);
  const [breakdown, setBreakdown] = useState<CategoryBreakdown[]>([]);
  const [netWorth, setNetWorth] = useState<NetWorthPoint[]>([]);

  useEffect(() => {
    api.monthlySummary(6).then(setMonthly);
    api.categoryBreakdown().then(setBreakdown);
    api.netWorth(12).then(setNetWorth);
  }, []);

  const barData = monthly.map((m) => ({
    month: m.month.slice(5),
    Ingresos: Number(m.income),
    Gastos: Number(m.expense),
  }));

  const pieData = breakdown.map((b, i) => ({
    name: b.category_name,
    value: Number(b.total),
    color: b.category_color || CHART_COLORS[i % CHART_COLORS.length],
  }));

  const lineData = netWorth.map((p) => ({
    month: p.month.slice(5),
    Patrimonio: Number(p.total),
  }));

  const totalExpense = breakdown.reduce((s, b) => s + Number(b.total), 0);

  return (
    <div className="max-w-[1440px] mx-auto">
      <Topbar title="Informes" subtitle="Analisis detallado de ingresos, gastos y tendencias." />

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {/* Monthly income vs expense */}
        <PageSection title="Ingresos vs Gastos" subtitle="Comparativa mensual de los ultimos 6 meses.">
          {barData.length > 0 ? (
            <div className="h-[300px]">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={barData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#ffffff10" />
                  <XAxis dataKey="month" stroke="#9fb0d1" fontSize={12} />
                  <YAxis stroke="#9fb0d1" fontSize={12} tickFormatter={(v) => `${v}`} />
                  <Tooltip
                    contentStyle={{ backgroundColor: '#0d1526', border: '1px solid #1e293b', borderRadius: '12px' }}
                    labelStyle={{ color: '#9fb0d1' }}
                    formatter={(value) => money(String(value))}
                  />
                  <Bar dataKey="Ingresos" fill="#56d364" radius={[4, 4, 0, 0]} />
                  <Bar dataKey="Gastos" fill="#ef4444" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          ) : (
            <div className="flex items-center justify-center py-12 text-muted-foreground">Sin datos suficientes</div>
          )}
        </PageSection>

        {/* Category breakdown */}
        <PageSection title="Gasto por categoria" subtitle="Distribucion del gasto del mes actual.">
          {pieData.length > 0 ? (
            <div className="flex gap-4">
              <div className="h-[300px] flex-1">
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie
                      data={pieData}
                      cx="50%"
                      cy="50%"
                      innerRadius={60}
                      outerRadius={100}
                      paddingAngle={2}
                      dataKey="value"
                    >
                      {pieData.map((entry, index) => (
                        <Cell key={index} fill={entry.color} />
                      ))}
                    </Pie>
                    <Tooltip
                      contentStyle={{ backgroundColor: '#0d1526', border: '1px solid #1e293b', borderRadius: '12px' }}
                      formatter={(value) => money(String(value))}
                    />
                  </PieChart>
                </ResponsiveContainer>
              </div>
              <div className="flex flex-col gap-2 justify-center min-w-[150px]">
                {breakdown.slice(0, 8).map((b, i) => (
                  <div key={i} className="flex items-center gap-2 text-sm">
                    <div className="w-2.5 h-2.5 rounded-full flex-shrink-0" style={{ backgroundColor: b.category_color || CHART_COLORS[i % CHART_COLORS.length] }} />
                    <span className="text-muted-foreground truncate">{b.category_name}</span>
                    <span className="text-foreground ml-auto whitespace-nowrap">{b.percentage}%</span>
                  </div>
                ))}
              </div>
            </div>
          ) : (
            <div className="flex items-center justify-center py-12 text-muted-foreground">Sin gastos categorizados este mes</div>
          )}
        </PageSection>
      </div>

      {/* Net worth evolution */}
      <div className="mt-4">
        <PageSection title="Evolucion del patrimonio" subtitle="Balance total acumulado a lo largo del tiempo.">
          {lineData.length > 0 ? (
            <div className="h-[300px]">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={lineData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#ffffff10" />
                  <XAxis dataKey="month" stroke="#9fb0d1" fontSize={12} />
                  <YAxis stroke="#9fb0d1" fontSize={12} tickFormatter={(v) => `${v}`} />
                  <Tooltip
                    contentStyle={{ backgroundColor: '#0d1526', border: '1px solid #1e293b', borderRadius: '12px' }}
                    labelStyle={{ color: '#9fb0d1' }}
                    formatter={(value) => money(String(value))}
                  />
                  <Line type="monotone" dataKey="Patrimonio" stroke="#6ea8fe" strokeWidth={2} dot={{ fill: '#6ea8fe', r: 4 }} />
                </LineChart>
              </ResponsiveContainer>
            </div>
          ) : (
            <div className="flex items-center justify-center py-12 text-muted-foreground">Sin datos suficientes</div>
          )}
        </PageSection>
      </div>
    </div>
  );
}
