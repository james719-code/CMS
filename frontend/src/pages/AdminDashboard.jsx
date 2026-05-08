import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { Building2, CalendarDays, Check, FileBarChart, Megaphone, Shield, Users, X } from 'lucide-react';
import StatCard from '../components/StatCard';
import DataTable from '../components/DataTable';
import Modal from '../components/Modal';
import ConfirmDialog from '../components/ConfirmDialog';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Empty, EmptyDescription, EmptyHeader, EmptyMedia, EmptyTitle } from '@/components/ui/empty';
import { Select, SelectContent, SelectGroup, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { useOrganizations } from '../hooks/useOrganizations';
import { useStatistics } from '../hooks/useStatistics';

const statusVariant = {
    active: 'default',
    pending: 'secondary',
    suspended: 'destructive',
    rejected: 'outline',
};

const StatusBadge = ({ status }) => (
    <Badge variant={statusVariant[status] || 'outline'} className="capitalize">
        {status || 'unknown'}
    </Badge>
);

const AdminDashboard = () => {
    const [activeTab, setActiveTab] = useState('overview');
    const [statusFilter, setStatusFilter] = useState('');
    const [selectedOrg, setSelectedOrg] = useState(null);
    const [showConfirmDialog, setShowConfirmDialog] = useState(false);
    const [confirmAction, setConfirmAction] = useState(null);

    const { stats, loading: statsLoading } = useStatistics('admin');
    const {
        organizations,
        loading: orgsLoading,
        approveOrg,
        rejectOrg,
        suspendOrg,
        reactivateOrg,
    } = useOrganizations({ status: statusFilter });

    const pendingOrgs = organizations.filter(org => org.status === 'pending');
    const activeOrgs = organizations.filter(org => org.status === 'active');

    const handleAction = (action, org) => {
        setSelectedOrg(org);
        setConfirmAction(action);
        setShowConfirmDialog(true);
    };

    const executeAction = async () => {
        if (!selectedOrg || !confirmAction) return;

        if (confirmAction === 'approve') await approveOrg(selectedOrg.id);
        if (confirmAction === 'reject') await rejectOrg(selectedOrg.id);
        if (confirmAction === 'suspend') await suspendOrg(selectedOrg.id);
        if (confirmAction === 'reactivate') await reactivateOrg(selectedOrg.id);

        setSelectedOrg(null);
        setConfirmAction(null);
    };

    const orgColumns = [
        { header: 'Name', accessor: 'name' },
        { header: 'Acronym', accessor: 'acronym' },
        { header: 'Leader', accessor: row => row.leader_name || 'N/A' },
        { header: 'Members', accessor: 'member_count' },
        {
            header: 'Status',
            accessor: 'status',
            render: row => <StatusBadge status={row.status} />
        },
        {
            header: 'Actions',
            sortable: false,
            render: row => (
                <div className="flex gap-2">
                    {row.status === 'pending' && (
                        <>
                            <Button
                                size="xs"
                                onClick={(e) => {
                                    e.stopPropagation();
                                    handleAction('approve', row);
                                }}
                            >
                                <Check data-icon="inline-start" />
                                Approve
                            </Button>
                            <Button
                                size="xs"
                                variant="destructive"
                                onClick={(e) => {
                                    e.stopPropagation();
                                    handleAction('reject', row);
                                }}
                            >
                                <X data-icon="inline-start" />
                                Reject
                            </Button>
                        </>
                    )}
                    {row.status === 'active' && (
                        <Button
                            size="xs"
                            variant="outline"
                            onClick={(e) => {
                                e.stopPropagation();
                                handleAction('suspend', row);
                            }}
                        >
                            Suspend
                        </Button>
                    )}
                    {row.status === 'suspended' && (
                        <Button
                            size="xs"
                            variant="outline"
                            onClick={(e) => {
                                e.stopPropagation();
                                handleAction('reactivate', row);
                            }}
                        >
                            Reactivate
                        </Button>
                    )}
                </div>
            )
        }
    ];

    const tabs = [
        { id: 'overview', label: 'Overview' },
        { id: 'organizations', label: 'Organizations' },
        { id: 'users', label: 'Users' },
        { id: 'announcements', label: 'Announcements' },
        { id: 'reports', label: 'Reports' },
    ];

    return (
        <div className="flex flex-col gap-6">
            <section className="flex flex-col gap-4 md:flex-row md:items-start md:justify-between">
                <div>
                    <p className="text-sm font-medium text-primary">Administration</p>
                    <h1 className="mt-2 text-3xl font-semibold tracking-tight">Admin Dashboard</h1>
                    <p className="mt-2 text-sm text-muted-foreground">Manage organizations, users, approvals, and system reporting.</p>
                </div>
                <Badge variant="outline" className="w-fit">System overview</Badge>
            </section>

            <Tabs value={activeTab} onValueChange={setActiveTab} className="flex flex-col gap-5">
                <TabsList className="w-fit max-w-full overflow-x-auto">
                    {tabs.map(tab => <TabsTrigger key={tab.id} value={tab.id}>{tab.label}</TabsTrigger>)}
                </TabsList>

                <TabsContent value="overview" className="m-0 flex flex-col gap-6">
                    <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
                        <StatCard
                            title="Total Organizations"
                            value={statsLoading ? '...' : (stats?.total_organizations || 0)}
                            subtitle={`${stats?.pending_organizations || 0} pending approval`}
                            color="maroon"
                            icon={<Building2 />}
                        />
                        <StatCard title="Active Organizations" value={stats?.active_organizations || 0} color="green" icon={<Shield />} />
                        <StatCard title="Total Users" value={stats?.total_users || 0} color="blue" icon={<Users />} />
                        <StatCard title="Total Events" value={stats?.total_events || 0} color="yellow" icon={<CalendarDays />} />
                    </div>

                    <Card className="shadow-none">
                        <CardHeader className="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
                            <div>
                                <CardTitle>Pending Approvals</CardTitle>
                                <CardDescription>Review new organization applications.</CardDescription>
                            </div>
                            <Badge variant="secondary">{pendingOrgs.length} pending</Badge>
                        </CardHeader>
                        <CardContent className="flex flex-col gap-3">
                            {pendingOrgs.length === 0 ? (
                                <Empty className="border">
                                    <EmptyHeader>
                                        <EmptyMedia variant="icon"><Check /></EmptyMedia>
                                        <EmptyTitle>No pending approvals</EmptyTitle>
                                        <EmptyDescription>New organization applications will appear here.</EmptyDescription>
                                    </EmptyHeader>
                                </Empty>
                            ) : pendingOrgs.slice(0, 5).map(org => (
                                <div key={org.id} className="flex flex-col gap-4 rounded-lg border p-4 md:flex-row md:items-center md:justify-between">
                                    <div className="flex items-center gap-3">
                                        <div className="flex size-11 items-center justify-center rounded-lg bg-primary/10 font-semibold text-primary">
                                            {org.acronym?.substring(0, 2)}
                                        </div>
                                        <div>
                                            <p className="font-medium">{org.name}</p>
                                            <p className="text-sm text-muted-foreground">Leader: {org.leader_name}</p>
                                        </div>
                                    </div>
                                    <div className="flex gap-2">
                                        <Button size="sm" onClick={() => handleAction('approve', org)}>
                                            <Check data-icon="inline-start" />
                                            Approve
                                        </Button>
                                        <Button size="sm" variant="destructive" onClick={() => handleAction('reject', org)}>
                                            <X data-icon="inline-start" />
                                            Reject
                                        </Button>
                                    </div>
                                </div>
                            ))}
                        </CardContent>
                    </Card>

                    <div className="grid gap-4 lg:grid-cols-2">
                        <Card className="shadow-none">
                            <CardHeader>
                                <CardTitle>Recent Active Organizations</CardTitle>
                                <CardDescription>Current approved organizations.</CardDescription>
                            </CardHeader>
                            <CardContent className="flex flex-col gap-3">
                                {activeOrgs.slice(0, 5).map(org => (
                                    <div key={org.id} className="flex items-center justify-between gap-4 rounded-lg border p-3">
                                        <div className="flex min-w-0 items-center gap-3">
                                            <div className="flex size-8 items-center justify-center rounded-md bg-emerald-50 text-xs font-semibold text-emerald-700">
                                                {org.acronym?.substring(0, 2)}
                                            </div>
                                            <span className="truncate text-sm font-medium">{org.name}</span>
                                        </div>
                                        <span className="text-sm text-muted-foreground">{org.member_count} members</span>
                                    </div>
                                ))}
                            </CardContent>
                        </Card>

                        <Card className="shadow-none">
                            <CardHeader>
                                <CardTitle>System Summary</CardTitle>
                                <CardDescription>Membership and organization health.</CardDescription>
                            </CardHeader>
                            <CardContent className="flex flex-col gap-4">
                                <SummaryRow label="Total Memberships" value={stats?.total_members || 0} />
                                <SummaryRow label="Pending Organizations" value={stats?.pending_organizations || 0} />
                                <SummaryRow label="Active Organizations" value={stats?.active_organizations || 0} />
                            </CardContent>
                        </Card>
                    </div>
                </TabsContent>

                <TabsContent value="organizations" className="m-0 flex flex-col gap-4">
                    <div className="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
                        <div>
                            <h2 className="text-lg font-semibold">Organizations</h2>
                            <p className="text-sm text-muted-foreground">Search, filter, and manage organization statuses.</p>
                        </div>
                        <Select value={statusFilter || 'all'} onValueChange={(value) => setStatusFilter(value === 'all' ? '' : value)}>
                            <SelectTrigger className="w-full md:w-48">
                                <SelectValue placeholder="All Status" />
                            </SelectTrigger>
                            <SelectContent>
                                <SelectGroup>
                                    <SelectItem value="all">All Status</SelectItem>
                                    <SelectItem value="active">Active</SelectItem>
                                    <SelectItem value="pending">Pending</SelectItem>
                                    <SelectItem value="suspended">Suspended</SelectItem>
                                    <SelectItem value="rejected">Rejected</SelectItem>
                                </SelectGroup>
                            </SelectContent>
                        </Select>
                    </div>
                    <DataTable
                        columns={orgColumns}
                        data={organizations}
                        loading={orgsLoading}
                        searchPlaceholder="Search organizations..."
                        onRowClick={(row) => setSelectedOrg(row)}
                    />
                </TabsContent>

                <TabsContent value="users" className="m-0">
                    <PlaceholderPanel
                        icon={<Users />}
                        title="User Management"
                        description="User management interface - view and manage all registered users."
                        to="/admin/users"
                        action="Manage Users"
                    />
                </TabsContent>

                <TabsContent value="announcements" className="m-0">
                    <PlaceholderPanel
                        icon={<Megaphone />}
                        title="System Announcements"
                        description="Create and manage system-wide announcements."
                        to="/admin/announcements"
                        action="Manage Announcements"
                    />
                </TabsContent>

                <TabsContent value="reports" className="m-0">
                    <PlaceholderPanel
                        icon={<FileBarChart />}
                        title="System Reports"
                        description="View analytics and generate reports."
                        to="/admin/reports"
                        action="View Reports"
                    />
                </TabsContent>
            </Tabs>

            <Modal
                isOpen={!!selectedOrg && !showConfirmDialog}
                onClose={() => setSelectedOrg(null)}
                title={selectedOrg?.name || 'Organization Details'}
                size="lg"
                description="Review organization metadata and current status."
            >
                {selectedOrg && (
                    <div className="grid gap-4 md:grid-cols-2">
                        <DetailItem label="Acronym" value={selectedOrg.acronym} />
                        <div>
                            <p className="text-sm text-muted-foreground">Status</p>
                            <div className="mt-1"><StatusBadge status={selectedOrg.status} /></div>
                        </div>
                        <DetailItem label="Leader" value={selectedOrg.leader_name} />
                        <DetailItem label="Members" value={selectedOrg.member_count} />
                    </div>
                )}
            </Modal>

            <ConfirmDialog
                isOpen={showConfirmDialog}
                onClose={() => {
                    setShowConfirmDialog(false);
                    setConfirmAction(null);
                }}
                onConfirm={executeAction}
                title={`${confirmAction?.charAt(0).toUpperCase()}${confirmAction?.slice(1)} Organization`}
                message={`Are you sure you want to ${confirmAction} "${selectedOrg?.name}"?`}
                confirmText={confirmAction?.charAt(0).toUpperCase() + confirmAction?.slice(1)}
                variant={confirmAction === 'reject' || confirmAction === 'suspend' ? 'danger' : 'success'}
            />
        </div>
    );
};

const SummaryRow = ({ label, value }) => (
    <div className="flex items-center justify-between gap-4">
        <span className="text-sm text-muted-foreground">{label}</span>
        <span className="font-semibold">{value}</span>
    </div>
);

const DetailItem = ({ label, value }) => (
    <div>
        <p className="text-sm text-muted-foreground">{label}</p>
        <p className="mt-1 font-medium">{value || 'N/A'}</p>
    </div>
);

const PlaceholderPanel = ({ icon, title, description, to, action }) => (
    <Card className="shadow-none">
        <CardContent className="flex flex-col gap-4 p-6">
            <div className="flex size-10 items-center justify-center rounded-lg bg-primary/10 text-primary">
                {icon}
            </div>
            <div>
                <h2 className="text-lg font-semibold">{title}</h2>
                <p className="mt-1 text-sm text-muted-foreground">{description}</p>
            </div>
            <Button asChild className="w-fit">
                <Link to={to}>{action}</Link>
            </Button>
        </CardContent>
    </Card>
);

export default AdminDashboard;
