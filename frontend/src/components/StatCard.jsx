import React from 'react';
import { ArrowDownRight, ArrowUpRight } from 'lucide-react';
import { Card, CardContent } from '@/components/ui/card';
import { cn } from '@/lib/utils';

const toneClasses = {
    blue: 'bg-sky-50 text-sky-700 border-sky-100',
    green: 'bg-emerald-50 text-emerald-700 border-emerald-100',
    yellow: 'bg-amber-50 text-amber-700 border-amber-100',
    red: 'bg-rose-50 text-rose-700 border-rose-100',
    purple: 'bg-violet-50 text-violet-700 border-violet-100',
    indigo: 'bg-indigo-50 text-indigo-700 border-indigo-100',
    maroon: 'bg-primary/10 text-primary border-primary/15',
};

const StatCard = ({ title, value, subtitle, icon, color = 'maroon', trend, onClick }) => {
    const TrendIcon = trend?.positive ? ArrowUpRight : ArrowDownRight;

    return (
        <Card
            className={cn(
                'border-border/80 bg-card shadow-none transition-colors hover:border-primary/25',
                onClick && 'cursor-pointer'
            )}
            onClick={onClick}
        >
            <CardContent className="flex items-start justify-between gap-4 p-5">
                <div className="min-w-0">
                    <p className="text-sm font-medium text-muted-foreground">{title}</p>
                    <p className="mt-2 text-2xl font-semibold tracking-tight text-foreground">{value}</p>
                    {subtitle && (
                        <p className="mt-1 text-sm text-muted-foreground">{subtitle}</p>
                    )}
                    {trend && (
                        <div
                            className={cn(
                                'mt-3 inline-flex items-center gap-1 text-xs font-medium',
                                trend.positive ? 'text-emerald-700' : 'text-rose-700'
                            )}
                        >
                            <TrendIcon />
                            <span>{trend.value}</span>
                            <span className="text-muted-foreground">{trend.label}</span>
                        </div>
                    )}
                </div>
                {icon && (
                    <div className={cn('flex size-10 shrink-0 items-center justify-center rounded-lg border', toneClasses[color] || toneClasses.maroon)}>
                        {icon}
                    </div>
                )}
            </CardContent>
        </Card>
    );
};

export default StatCard;
