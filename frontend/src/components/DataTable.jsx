import React, { useMemo, useState } from 'react';
import { ArrowDown, ArrowUp, Search } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Empty, EmptyDescription, EmptyHeader, EmptyMedia, EmptyTitle } from '@/components/ui/empty';
import { Input } from '@/components/ui/input';
import { Skeleton } from '@/components/ui/skeleton';
import {
    Table,
    TableBody,
    TableCell,
    TableHead,
    TableHeader,
    TableRow,
} from '@/components/ui/table';
import { cn } from '@/lib/utils';

const DataTable = ({
    columns,
    data,
    loading = false,
    searchable = true,
    searchPlaceholder = 'Search...',
    pageSize = 10,
    onRowClick,
    emptyMessage = 'No data available'
}) => {
    const [searchTerm, setSearchTerm] = useState('');
    const [currentPage, setCurrentPage] = useState(1);
    const [sortConfig, setSortConfig] = useState({ key: null, direction: 'asc' });

    const filteredData = useMemo(() => {
        return data.filter(row =>
            columns.some(col => {
                const value = col.accessor
                    ? (typeof col.accessor === 'function' ? col.accessor(row) : row[col.accessor])
                    : '';
                return String(value).toLowerCase().includes(searchTerm.toLowerCase());
            })
        );
    }, [columns, data, searchTerm]);

    const sortedData = useMemo(() => {
        return [...filteredData].sort((a, b) => {
            if (!sortConfig.key) return 0;
            const col = columns.find(c => c.accessor === sortConfig.key);
            const aVal = col?.accessor ? (typeof col.accessor === 'function' ? col.accessor(a) : a[col.accessor]) : '';
            const bVal = col?.accessor ? (typeof col.accessor === 'function' ? col.accessor(b) : b[col.accessor]) : '';

            if (aVal < bVal) return sortConfig.direction === 'asc' ? -1 : 1;
            if (aVal > bVal) return sortConfig.direction === 'asc' ? 1 : -1;
            return 0;
        });
    }, [columns, filteredData, sortConfig]);

    const totalPages = Math.ceil(sortedData.length / pageSize);
    const paginatedData = sortedData.slice((currentPage - 1) * pageSize, currentPage * pageSize);

    const handleSort = (key) => {
        setSortConfig(prev => ({
            key,
            direction: prev.key === key && prev.direction === 'asc' ? 'desc' : 'asc'
        }));
    };

    return (
        <Card className="overflow-hidden border-border/80 shadow-none">
            {searchable && (
                <div className="border-b bg-muted/20 p-3">
                    <div className="relative max-w-sm">
                        <Search className="pointer-events-none absolute left-2.5 top-1/2 -translate-y-1/2 text-muted-foreground" />
                        <Input
                            type="text"
                            placeholder={searchPlaceholder}
                            value={searchTerm}
                            onChange={(e) => {
                                setSearchTerm(e.target.value);
                                setCurrentPage(1);
                            }}
                            className="pl-8"
                        />
                    </div>
                </div>
            )}

            <div className="overflow-x-auto">
                <Table>
                    <TableHeader>
                        <TableRow className="bg-muted/30 hover:bg-muted/30">
                            {columns.map((col, idx) => {
                                const isSorted = sortConfig.key === col.accessor;
                                const SortIcon = sortConfig.direction === 'asc' ? ArrowUp : ArrowDown;

                                return (
                                    <TableHead
                                        key={idx}
                                        className={cn(
                                            'h-10 whitespace-nowrap text-xs font-semibold uppercase tracking-normal text-muted-foreground',
                                            col.sortable !== false && 'cursor-pointer select-none hover:text-foreground'
                                        )}
                                        onClick={() => col.sortable !== false && handleSort(col.accessor)}
                                    >
                                        <div className="flex items-center gap-1.5">
                                            {col.header}
                                            {isSorted && <SortIcon />}
                                        </div>
                                    </TableHead>
                                );
                            })}
                        </TableRow>
                    </TableHeader>
                    <TableBody>
                        {loading ? (
                            Array.from({ length: 4 }).map((_, rowIdx) => (
                                <TableRow key={rowIdx}>
                                    {columns.map((_, colIdx) => (
                                        <TableCell key={colIdx}>
                                            <Skeleton className="h-4 w-full max-w-32" />
                                        </TableCell>
                                    ))}
                                </TableRow>
                            ))
                        ) : paginatedData.length === 0 ? (
                            <TableRow>
                                <TableCell colSpan={columns.length}>
                                    <Empty className="border-0 py-10">
                                        <EmptyHeader>
                                            <EmptyMedia variant="icon">
                                                <Search />
                                            </EmptyMedia>
                                            <EmptyTitle>No results</EmptyTitle>
                                            <EmptyDescription>{emptyMessage}</EmptyDescription>
                                        </EmptyHeader>
                                    </Empty>
                                </TableCell>
                            </TableRow>
                        ) : (
                            paginatedData.map((row, rowIdx) => (
                                <TableRow
                                    key={row.id || rowIdx}
                                    className={cn(onRowClick && 'cursor-pointer')}
                                    onClick={() => onRowClick && onRowClick(row)}
                                >
                                    {columns.map((col, colIdx) => (
                                        <TableCell key={colIdx} className="whitespace-nowrap text-sm">
                                            {col.render ? col.render(row) : (typeof col.accessor === 'function' ? col.accessor(row) : row[col.accessor])}
                                        </TableCell>
                                    ))}
                                </TableRow>
                            ))
                        )}
                    </TableBody>
                </Table>
            </div>

            {totalPages > 1 && (
                <div className="flex items-center justify-between border-t px-4 py-3">
                    <p className="text-sm text-muted-foreground">
                        Showing {((currentPage - 1) * pageSize) + 1} to {Math.min(currentPage * pageSize, sortedData.length)} of {sortedData.length}
                    </p>
                    <div className="flex gap-2">
                        <Button
                            variant="outline"
                            size="sm"
                            onClick={() => setCurrentPage(p => Math.max(1, p - 1))}
                            disabled={currentPage === 1}
                        >
                            Previous
                        </Button>
                        <Button
                            variant="outline"
                            size="sm"
                            onClick={() => setCurrentPage(p => Math.min(totalPages, p + 1))}
                            disabled={currentPage === totalPages}
                        >
                            Next
                        </Button>
                    </div>
                </div>
            )}
        </Card>
    );
};

export default DataTable;
