import React, { useEffect, useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import { toast } from 'sonner';
import {
    BadgeDollarSign,
    CalendarDays,
    Check,
    FileText,
    Megaphone,
    Plus,
    Trash2,
    Upload,
    UserCheck,
    Users,
    X,
} from 'lucide-react';
import api from '../../api/axios';
import StatCard from '../../components/StatCard';
import DataTable from '../../components/DataTable';
import Modal from '../../components/Modal';
import ConfirmDialog from '../../components/ConfirmDialog';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Empty, EmptyDescription, EmptyHeader, EmptyMedia, EmptyTitle } from '@/components/ui/empty';
import { Field, FieldGroup, FieldLabel } from '@/components/ui/field';
import { Input } from '@/components/ui/input';
import { Select, SelectContent, SelectGroup, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Textarea } from '@/components/ui/textarea';
import { useStatistics } from '../../hooks/useStatistics';
import { useMembers } from '../../hooks/useMembers';
import { useMembershipRequests } from '../../hooks/useMembershipRequests';
import { useEvents } from '../../hooks/useEvents';
import { useBudget } from '../../hooks/useBudget';
import { useAnnouncements } from '../../hooks/useAnnouncements';
import { useDocuments } from '../../hooks/useDocuments';
import { cn } from '@/lib/utils';

const formatCurrency = (value) => `PHP ${Number(value || 0).toLocaleString()}`;
const formatDate = (date) => date ? new Date(date).toLocaleDateString() : 'TBA';

const OfficerDashboard = () => {
    const { orgId } = useParams();
    const [organization, setOrganization] = useState(null);
    const [activeTab, setActiveTab] = useState('overview');
    const [showModal, setShowModal] = useState(false);
    const [modalType, setModalType] = useState(null);
    const [showConfirm, setShowConfirm] = useState(false);
    const [selectedItem, setSelectedItem] = useState(null);

    const { stats } = useStatistics('officer', orgId);
    const { members, loading: membersLoading, promoteMember, demoteMember, deactivateMember } = useMembers(orgId);
    const { pendingRequests, approveRequest, rejectRequest } = useMembershipRequests(orgId);
    const { events, loading: eventsLoading, createEvent, deleteEvent } = useEvents(orgId);
    const { budgets, summary, addBudgetEntry, deleteBudgetEntry } = useBudget(orgId);
    const { announcements, createAnnouncement, deleteAnnouncement, pinAnnouncement, unpinAnnouncement } = useAnnouncements(orgId);
    const { documents, loading: documentsLoading, uploadDocument, deleteDocument } = useDocuments(orgId);

    const [eventForm, setEventForm] = useState({ title: '', description: '', venue: '', start_time: '', end_time: '' });
    const [budgetForm, setBudgetForm] = useState({ transaction_type: 'income', amount: '', description: '', date: '' });
    const [announcementForm, setAnnouncementForm] = useState({ title: '', content: '' });
    const [documentForm, setDocumentForm] = useState({ title: '', file: null });

    useEffect(() => {
        const fetchOrg = async () => {
            try {
                const res = await api.get(`/api/organizations/${orgId}/`);
                setOrganization(res.data);
            } catch (err) {
                console.error('Failed to fetch organization', err);
                toast.error('Failed to load organization');
            }
        };
        if (orgId) fetchOrg();
    }, [orgId]);

    const tabs = [
        { id: 'overview', label: 'Overview' },
        { id: 'members', label: 'Members' },
        { id: 'requests', label: 'Requests' },
        { id: 'events', label: 'Events' },
        { id: 'budget', label: 'Budget' },
        { id: 'announcements', label: 'Announcements' },
        { id: 'documents', label: 'Documents' },
    ];

    const memberColumns = [
        { header: 'Name', accessor: row => row.user_details?.full_name || row.user_details?.email },
        { header: 'Email', accessor: row => row.user_details?.email },
        {
            header: 'Role',
            accessor: 'role',
            render: row => (
                <Badge variant={row.role === 'officer' ? 'default' : 'secondary'} className="capitalize">
                    {row.role} {row.position && `- ${row.position}`}
                </Badge>
            )
        },
        { header: 'Joined', accessor: row => formatDate(row.date_joined) },
        {
            header: 'Actions',
            sortable: false,
            render: row => (
                <div className="flex gap-2">
                    {row.role === 'member' ? (
                        <Button size="xs" variant="outline" onClick={() => promoteMember(row.id)}>Promote</Button>
                    ) : (
                        <Button size="xs" variant="outline" onClick={() => demoteMember(row.id)}>Demote</Button>
                    )}
                    <Button
                        size="xs"
                        variant="destructive"
                        onClick={() => {
                            setSelectedItem(row);
                            setShowConfirm(true);
                        }}
                    >
                        Remove
                    </Button>
                </div>
            )
        }
    ];

    const eventColumns = [
        { header: 'Title', accessor: 'title' },
        { header: 'Venue', accessor: 'venue' },
        { header: 'Date', accessor: row => formatDate(row.start_time) },
        { header: 'Attendees', accessor: 'attendee_count' },
        {
            header: 'Actions',
            sortable: false,
            render: row => (
                <div className="flex gap-2">
                    <Button asChild size="xs" variant="outline">
                        <Link to={`/officer/${orgId}/events/${row.id}/attendance`}>Attendance</Link>
                    </Button>
                    <Button size="xs" variant="destructive" onClick={() => deleteEvent(row.id)}>Delete</Button>
                </div>
            )
        }
    ];

    const openModal = (type) => {
        setModalType(type);
        setShowModal(true);
    };

    const closeModal = () => {
        setShowModal(false);
        setModalType(null);
    };

    const handleCreateEvent = async (e) => {
        e.preventDefault();
        try {
            await createEvent({ ...eventForm, organization: orgId });
            setEventForm({ title: '', description: '', venue: '', start_time: '', end_time: '' });
            closeModal();
            toast.success('Event created');
        } catch (err) {
            toast.error(err.response?.data?.error || 'Failed to create event');
        }
    };

    const handleAddBudget = async (e) => {
        e.preventDefault();
        try {
            await addBudgetEntry(budgetForm);
            setBudgetForm({ transaction_type: 'income', amount: '', description: '', date: '' });
            closeModal();
            toast.success('Budget entry added');
        } catch (err) {
            toast.error(err.response?.data?.error || 'Failed to add budget entry');
        }
    };

    const handleCreateAnnouncement = async (e) => {
        e.preventDefault();
        try {
            await createAnnouncement(announcementForm);
            setAnnouncementForm({ title: '', content: '' });
            closeModal();
            toast.success('Announcement posted');
        } catch (err) {
            toast.error(err.response?.data?.error || 'Failed to post announcement');
        }
    };

    const handleUploadDocument = async (e) => {
        e.preventDefault();
        if (!documentForm.file) {
            toast.error('Choose a document to upload');
            return;
        }
        try {
            const formData = new FormData();
            formData.append('title', documentForm.title);
            formData.append('file', documentForm.file);
            await uploadDocument(formData);
            setDocumentForm({ title: '', file: null });
            closeModal();
            toast.success('Document uploaded');
        } catch (err) {
            toast.error(err.response?.data?.error || 'Failed to upload document');
        }
    };

    if (!organization) {
        return (
            <div className="flex h-64 items-center justify-center text-sm text-muted-foreground">
                Loading organization...
            </div>
        );
    }

    return (
        <div className="flex flex-col gap-6">
            <section className="flex flex-col gap-4 md:flex-row md:items-start md:justify-between">
                <div>
                    <p className="text-sm font-medium text-primary">{organization.acronym} · Officer Dashboard</p>
                    <h1 className="mt-2 text-3xl font-semibold tracking-tight">{organization.name}</h1>
                    <p className="mt-2 text-sm text-muted-foreground">Manage members, requests, events, budget, announcements, and documents.</p>
                </div>
                <Button asChild variant="outline">
                    <Link to={`/officer/${orgId}/profile`}>Edit Profile</Link>
                </Button>
            </section>

            <Tabs value={activeTab} onValueChange={setActiveTab} className="flex flex-col gap-5">
                <TabsList className="w-fit max-w-full overflow-x-auto">
                    {tabs.map(tab => <TabsTrigger key={tab.id} value={tab.id}>{tab.label}</TabsTrigger>)}
                </TabsList>

                <TabsContent value="overview" className="m-0 flex flex-col gap-6">
                    <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
                        <StatCard title="Members" value={stats?.member_count || 0} subtitle={`${stats?.officer_count || 0} officers`} color="maroon" icon={<Users />} />
                        <StatCard title="Pending Requests" value={stats?.pending_requests || 0} color="yellow" icon={<UserCheck />} />
                        <StatCard title="Upcoming Events" value={stats?.upcoming_events || 0} color="green" icon={<CalendarDays />} />
                        <StatCard title="Budget Balance" value={formatCurrency(stats?.budget_balance)} color="blue" icon={<BadgeDollarSign />} />
                    </div>

                    <div className="grid gap-4 lg:grid-cols-2">
                        <Card className="shadow-none">
                            <CardHeader>
                                <CardTitle>Recent Members</CardTitle>
                                <CardDescription>Newest people in this organization.</CardDescription>
                            </CardHeader>
                            <CardContent className="flex flex-col gap-3">
                                {members.slice(0, 5).map(m => (
                                    <div key={m.id} className="flex items-center justify-between gap-4 rounded-lg border p-3">
                                        <div>
                                            <p className="font-medium">{m.user_details?.full_name}</p>
                                            <p className="text-sm text-muted-foreground">{m.role}</p>
                                        </div>
                                    </div>
                                ))}
                            </CardContent>
                        </Card>

                        <Card className="shadow-none">
                            <CardHeader>
                                <CardTitle>Pending Requests</CardTitle>
                                <CardDescription>Students waiting for membership review.</CardDescription>
                            </CardHeader>
                            <CardContent className="flex flex-col gap-3">
                                {pendingRequests.length === 0 ? (
                                    <Empty className="border">
                                        <EmptyHeader>
                                            <EmptyMedia variant="icon"><Check /></EmptyMedia>
                                            <EmptyTitle>No pending requests</EmptyTitle>
                                            <EmptyDescription>Membership requests will appear here.</EmptyDescription>
                                        </EmptyHeader>
                                    </Empty>
                                ) : pendingRequests.slice(0, 5).map(req => (
                                    <div key={req.id} className="flex flex-col gap-3 rounded-lg border p-3 md:flex-row md:items-center md:justify-between">
                                        <div>
                                            <p className="font-medium">{req.user_details?.full_name}</p>
                                            <p className="text-sm text-muted-foreground">{req.message?.substring(0, 50) || req.user_details?.email}</p>
                                        </div>
                                        <div className="flex gap-2">
                                            <Button size="xs" onClick={() => approveRequest(req.id)}><Check data-icon="inline-start" />Approve</Button>
                                            <Button size="xs" variant="destructive" onClick={() => rejectRequest(req.id)}><X data-icon="inline-start" />Reject</Button>
                                        </div>
                                    </div>
                                ))}
                            </CardContent>
                        </Card>
                    </div>
                </TabsContent>

                <TabsContent value="members" className="m-0">
                    <DataTable columns={memberColumns} data={members} loading={membersLoading} searchPlaceholder="Search members..." />
                </TabsContent>

                <TabsContent value="requests" className="m-0 flex flex-col gap-4">
                    <SectionHeader title="Membership Requests" description="Approve or reject students who asked to join." />
                    {pendingRequests.length === 0 ? (
                        <Empty className="border bg-background">
                            <EmptyHeader>
                                <EmptyMedia variant="icon"><UserCheck /></EmptyMedia>
                                <EmptyTitle>No pending requests</EmptyTitle>
                                <EmptyDescription>New requests will appear here.</EmptyDescription>
                            </EmptyHeader>
                        </Empty>
                    ) : pendingRequests.map(req => (
                        <Card key={req.id} className="shadow-none">
                            <CardContent className="flex flex-col gap-4 p-5 md:flex-row md:items-center md:justify-between">
                                <div>
                                    <p className="font-medium">{req.user_details?.full_name}</p>
                                    <p className="text-sm text-muted-foreground">{req.user_details?.email}</p>
                                    {req.message && <p className="mt-2 text-sm leading-6 text-foreground/80">&quot;{req.message}&quot;</p>}
                                </div>
                                <div className="flex gap-2">
                                    <Button onClick={() => approveRequest(req.id)}><Check data-icon="inline-start" />Approve</Button>
                                    <Button variant="destructive" onClick={() => rejectRequest(req.id)}><X data-icon="inline-start" />Reject</Button>
                                </div>
                            </CardContent>
                        </Card>
                    ))}
                </TabsContent>

                <TabsContent value="events" className="m-0 flex flex-col gap-4">
                    <ActionHeader title="Events" description="Create activities and manage attendance." action="Create Event" onAction={() => openModal('event')} />
                    <DataTable columns={eventColumns} data={events} loading={eventsLoading} searchPlaceholder="Search events..." />
                </TabsContent>

                <TabsContent value="budget" className="m-0 flex flex-col gap-6">
                    <div className="grid gap-4 md:grid-cols-3">
                        <StatCard title="Total Income" value={formatCurrency(summary.total_income)} color="green" icon={<BadgeDollarSign />} />
                        <StatCard title="Total Expenses" value={formatCurrency(summary.total_expense)} color="red" icon={<BadgeDollarSign />} />
                        <StatCard title="Balance" value={formatCurrency(summary.balance)} color="maroon" icon={<BadgeDollarSign />} />
                    </div>
                    <ActionHeader title="Transactions" description="Track income and expenses for this organization." action="Add Entry" onAction={() => openModal('budget')} />
                    <Card className="overflow-hidden shadow-none">
                        <Table>
                            <TableHeader>
                                <TableRow className="bg-muted/30 hover:bg-muted/30">
                                    <TableHead>Date</TableHead>
                                    <TableHead>Type</TableHead>
                                    <TableHead>Description</TableHead>
                                    <TableHead className="text-right">Amount</TableHead>
                                    <TableHead className="text-right">Actions</TableHead>
                                </TableRow>
                            </TableHeader>
                            <TableBody>
                                {budgets.map(b => (
                                    <TableRow key={b.id}>
                                        <TableCell>{formatDate(b.date)}</TableCell>
                                        <TableCell>
                                            <Badge variant={b.transaction_type === 'income' ? 'default' : 'destructive'} className="capitalize">
                                                {b.transaction_type}
                                            </Badge>
                                        </TableCell>
                                        <TableCell>{b.description}</TableCell>
                                        <TableCell className={cn('text-right font-medium', b.transaction_type === 'income' ? 'text-emerald-700' : 'text-destructive')}>
                                            {b.transaction_type === 'income' ? '+' : '-'}{formatCurrency(b.amount)}
                                        </TableCell>
                                        <TableCell className="text-right">
                                            <Button size="xs" variant="destructive" onClick={() => deleteBudgetEntry(b.id)}>
                                                <Trash2 data-icon="inline-start" />
                                                Delete
                                            </Button>
                                        </TableCell>
                                    </TableRow>
                                ))}
                            </TableBody>
                        </Table>
                    </Card>
                </TabsContent>

                <TabsContent value="announcements" className="m-0 flex flex-col gap-4">
                    <ActionHeader title="Announcements" description="Publish updates for organization members." action="Create Announcement" onAction={() => openModal('announcement')} />
                    {announcements.length === 0 ? (
                        <Empty className="border bg-background">
                            <EmptyHeader>
                                <EmptyMedia variant="icon"><Megaphone /></EmptyMedia>
                                <EmptyTitle>No announcements</EmptyTitle>
                                <EmptyDescription>Create the first announcement for members.</EmptyDescription>
                            </EmptyHeader>
                        </Empty>
                    ) : announcements.map(a => (
                        <Card key={a.id} className={cn('shadow-none', a.is_pinned && 'border-amber-200')}>
                            <CardContent className="flex flex-col gap-4 p-5 md:flex-row md:items-start md:justify-between">
                                <div>
                                    <div className="flex flex-wrap items-center gap-2">
                                        <p className="font-medium">{a.title}</p>
                                        {a.is_pinned && <Badge variant="secondary">Pinned</Badge>}
                                    </div>
                                    <p className="mt-2 text-sm leading-6 text-foreground/80">{a.content}</p>
                                    <p className="mt-2 text-sm text-muted-foreground">{formatDate(a.created_at)}</p>
                                </div>
                                <div className="flex gap-2">
                                    <Button size="sm" variant="outline" onClick={() => a.is_pinned ? unpinAnnouncement(a.id) : pinAnnouncement(a.id)}>
                                        {a.is_pinned ? 'Unpin' : 'Pin'}
                                    </Button>
                                    <Button size="sm" variant="destructive" onClick={() => deleteAnnouncement(a.id)}>Delete</Button>
                                </div>
                            </CardContent>
                        </Card>
                    ))}
                </TabsContent>

                <TabsContent value="documents" className="m-0 flex flex-col gap-4">
                    <ActionHeader title="Documents" description="Upload and organize files for the organization." action="Upload Document" onAction={() => openModal('document')} />
                    {documents.length === 0 ? (
                        <Empty className="border bg-background">
                            <EmptyHeader>
                                <EmptyMedia variant="icon"><FileText /></EmptyMedia>
                                <EmptyTitle>No documents</EmptyTitle>
                                <EmptyDescription>Uploaded files will appear here.</EmptyDescription>
                            </EmptyHeader>
                        </Empty>
                    ) : (
                        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
                            {documents.map(doc => (
                                <Card key={doc.id} className="shadow-none">
                                    <CardContent className="flex items-start justify-between gap-4 p-5">
                                        <div className="flex min-w-0 items-center gap-3">
                                            <div className="flex size-10 items-center justify-center rounded-lg bg-primary/10 text-xs font-semibold text-primary">
                                                {doc.file_extension || 'FILE'}
                                            </div>
                                            <div className="min-w-0">
                                                <p className="truncate font-medium">{doc.title}</p>
                                                <p className="text-sm text-muted-foreground">{(doc.file_size / 1024).toFixed(1)} KB</p>
                                            </div>
                                        </div>
                                        <Button size="icon-sm" variant="destructive" onClick={() => deleteDocument(doc.id)} aria-label="Delete document">
                                            <Trash2 />
                                        </Button>
                                    </CardContent>
                                </Card>
                            ))}
                        </div>
                    )}
                    {documentsLoading && <p className="text-sm text-muted-foreground">Loading documents...</p>}
                </TabsContent>
            </Tabs>

            <Modal isOpen={showModal} onClose={closeModal} title={modalTitle(modalType)}>
                {modalType === 'event' && (
                    <form onSubmit={handleCreateEvent}>
                        <FieldGroup>
                            <Field>
                                <FieldLabel htmlFor="event-title">Event Title</FieldLabel>
                                <Input id="event-title" value={eventForm.title} onChange={e => setEventForm({ ...eventForm, title: e.target.value })} required />
                            </Field>
                            <Field>
                                <FieldLabel htmlFor="event-venue">Venue</FieldLabel>
                                <Input id="event-venue" value={eventForm.venue} onChange={e => setEventForm({ ...eventForm, venue: e.target.value })} required />
                            </Field>
                            <Field>
                                <FieldLabel htmlFor="event-description">Description</FieldLabel>
                                <Textarea id="event-description" value={eventForm.description} onChange={e => setEventForm({ ...eventForm, description: e.target.value })} rows={3} />
                            </Field>
                            <div className="grid gap-4 md:grid-cols-2">
                                <Field>
                                    <FieldLabel htmlFor="event-start">Start Time</FieldLabel>
                                    <Input id="event-start" type="datetime-local" value={eventForm.start_time} onChange={e => setEventForm({ ...eventForm, start_time: e.target.value })} required />
                                </Field>
                                <Field>
                                    <FieldLabel htmlFor="event-end">End Time</FieldLabel>
                                    <Input id="event-end" type="datetime-local" value={eventForm.end_time} onChange={e => setEventForm({ ...eventForm, end_time: e.target.value })} required />
                                </Field>
                            </div>
                            <Button type="submit" className="w-full">Create Event</Button>
                        </FieldGroup>
                    </form>
                )}
                {modalType === 'budget' && (
                    <form onSubmit={handleAddBudget}>
                        <FieldGroup>
                            <Field>
                                <FieldLabel>Type</FieldLabel>
                                <Select value={budgetForm.transaction_type} onValueChange={value => setBudgetForm({ ...budgetForm, transaction_type: value })}>
                                    <SelectTrigger><SelectValue /></SelectTrigger>
                                    <SelectContent>
                                        <SelectGroup>
                                            <SelectItem value="income">Income</SelectItem>
                                            <SelectItem value="expense">Expense</SelectItem>
                                        </SelectGroup>
                                    </SelectContent>
                                </Select>
                            </Field>
                            <Field>
                                <FieldLabel htmlFor="budget-amount">Amount</FieldLabel>
                                <Input id="budget-amount" type="number" value={budgetForm.amount} onChange={e => setBudgetForm({ ...budgetForm, amount: e.target.value })} required />
                            </Field>
                            <Field>
                                <FieldLabel htmlFor="budget-date">Date</FieldLabel>
                                <Input id="budget-date" type="date" value={budgetForm.date} onChange={e => setBudgetForm({ ...budgetForm, date: e.target.value })} required />
                            </Field>
                            <Field>
                                <FieldLabel htmlFor="budget-description">Description</FieldLabel>
                                <Textarea id="budget-description" value={budgetForm.description} onChange={e => setBudgetForm({ ...budgetForm, description: e.target.value })} required rows={3} />
                            </Field>
                            <Button type="submit" className="w-full">Add Entry</Button>
                        </FieldGroup>
                    </form>
                )}
                {modalType === 'announcement' && (
                    <form onSubmit={handleCreateAnnouncement}>
                        <FieldGroup>
                            <Field>
                                <FieldLabel htmlFor="announcement-title">Title</FieldLabel>
                                <Input id="announcement-title" value={announcementForm.title} onChange={e => setAnnouncementForm({ ...announcementForm, title: e.target.value })} required />
                            </Field>
                            <Field>
                                <FieldLabel htmlFor="announcement-content">Content</FieldLabel>
                                <Textarea id="announcement-content" value={announcementForm.content} onChange={e => setAnnouncementForm({ ...announcementForm, content: e.target.value })} required rows={5} />
                            </Field>
                            <Button type="submit" className="w-full">Post Announcement</Button>
                        </FieldGroup>
                    </form>
                )}
                {modalType === 'document' && (
                    <form onSubmit={handleUploadDocument}>
                        <FieldGroup>
                            <Field>
                                <FieldLabel htmlFor="document-title">Title</FieldLabel>
                                <Input id="document-title" value={documentForm.title} onChange={e => setDocumentForm({ ...documentForm, title: e.target.value })} required />
                            </Field>
                            <Field>
                                <FieldLabel htmlFor="document-file">File</FieldLabel>
                                <Input id="document-file" type="file" onChange={e => setDocumentForm({ ...documentForm, file: e.target.files?.[0] || null })} required />
                            </Field>
                            <Button type="submit" className="w-full">
                                <Upload data-icon="inline-start" />
                                Upload Document
                            </Button>
                        </FieldGroup>
                    </form>
                )}
            </Modal>

            <ConfirmDialog
                isOpen={showConfirm}
                onClose={() => setShowConfirm(false)}
                onConfirm={() => {
                    if (selectedItem) deactivateMember(selectedItem.id);
                }}
                title="Remove Member"
                message={`Are you sure you want to remove ${selectedItem?.user_details?.full_name} from the organization?`}
                confirmText="Remove"
                variant="danger"
            />
        </div>
    );
};

const SectionHeader = ({ title, description }) => (
    <div>
        <h2 className="text-lg font-semibold">{title}</h2>
        <p className="text-sm text-muted-foreground">{description}</p>
    </div>
);

const ActionHeader = ({ title, description, action, onAction }) => (
    <div className="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
        <SectionHeader title={title} description={description} />
        <Button onClick={onAction} className="w-fit">
            <Plus data-icon="inline-start" />
            {action}
        </Button>
    </div>
);

const modalTitle = (type) => {
    if (type === 'event') return 'Create Event';
    if (type === 'budget') return 'Add Budget Entry';
    if (type === 'announcement') return 'Create Announcement';
    if (type === 'document') return 'Upload Document';
    return 'Details';
};

export default OfficerDashboard;
