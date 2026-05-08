import React, { useCallback, useEffect, useMemo, useState } from 'react';
import { Link } from 'react-router-dom';
import { toast } from 'sonner';
import {
    Bell,
    Building2,
    CalendarDays,
    ClipboardList,
    MapPin,
    Megaphone,
    Plus,
    ShieldCheck,
    Users,
} from 'lucide-react';
import api from '../api/axios';
import StatCard from '../components/StatCard';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import {
    Dialog,
    DialogContent,
    DialogDescription,
    DialogFooter,
    DialogHeader,
    DialogTitle,
} from '@/components/ui/dialog';
import { Empty, EmptyDescription, EmptyHeader, EmptyMedia, EmptyTitle } from '@/components/ui/empty';
import { Field, FieldGroup, FieldLabel } from '@/components/ui/field';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Textarea } from '@/components/ui/textarea';
import { useAuth } from '../context/AuthContext';
import { cn } from '@/lib/utils';

const formatDate = (date) => date ? new Date(date).toLocaleDateString() : 'TBA';

const StudentDashboard = () => {
    const { user } = useAuth();
    const [memberships, setMemberships] = useState([]);
    const [availableOrgs, setAvailableOrgs] = useState([]);
    const [announcements, setAnnouncements] = useState([]);
    const [upcomingEvents, setUpcomingEvents] = useState([]);
    const [loading, setLoading] = useState(true);
    const [activeTab, setActiveTab] = useState('overview');
    const [joinMessage, setJoinMessage] = useState('');
    const [selectedOrg, setSelectedOrg] = useState(null);
    const [showJoinModal, setShowJoinModal] = useState(false);

    const fetchData = useCallback(async () => {
        try {
            setLoading(true);
            const [membershipsRes, orgsRes, announcementsRes, eventsRes] = await Promise.all([
                api.get('/api/memberships/'),
                api.get('/api/organizations/?status=active'),
                api.get('/api/announcements/'),
                api.get('/api/events/my_events/')
            ]);
            setMemberships(membershipsRes.data.filter(m => m.user === user?.id));
            setAvailableOrgs(orgsRes.data);
            setAnnouncements(announcementsRes.data);
            setUpcomingEvents(eventsRes.data);
        } catch (err) {
            console.error('Failed to fetch data', err);
            toast.error('Failed to load dashboard data');
        } finally {
            setLoading(false);
        }
    }, [user?.id]);

    useEffect(() => {
        fetchData();
    }, [fetchData]);

    const handleJoinRequest = async () => {
        if (!selectedOrg) return;
        try {
            await api.post('/api/membership-requests/', {
                organization: selectedOrg.id,
                message: joinMessage
            });
            toast.success('Join request sent');
            setShowJoinModal(false);
            setJoinMessage('');
            setSelectedOrg(null);
        } catch (err) {
            toast.error(err.response?.data?.error || 'Failed to send request');
        }
    };

    const myOrgIds = memberships.map(m => m.organization);
    const orgsToJoin = availableOrgs.filter(org => !myOrgIds.includes(org.id));
    const officerMemberships = memberships.filter(m => m.role === 'officer');
    const isLeader = user?.led_org_id && user?.led_org_status === 'active';

    const tabItems = [
        { id: 'overview', label: 'Overview' },
        { id: 'my-orgs', label: 'My Organizations' },
        { id: 'browse', label: 'Browse Organizations' },
        { id: 'events', label: 'Events' },
        { id: 'announcements', label: 'Announcements' },
    ];

    const featuredAnnouncements = useMemo(
        () => [...announcements].sort((a, b) => Number(b.is_pinned) - Number(a.is_pinned)).slice(0, 5),
        [announcements]
    );

    if (loading) {
        return (
            <div className="flex h-64 items-center justify-center text-sm text-muted-foreground">
                Loading dashboard...
            </div>
        );
    }

    return (
        <div className="flex flex-col gap-6">
            <section className="flex flex-col gap-4 md:flex-row md:items-start md:justify-between">
                <div>
                    <p className="text-sm font-medium text-primary">Student workspace</p>
                    <h1 className="mt-2 text-3xl font-semibold tracking-tight">Welcome, {user?.first_name}.</h1>
                    <p className="mt-2 text-sm text-muted-foreground">Track organizations, events, and announcements in one place.</p>
                </div>
                {!user?.led_org_id && (
                    <Button asChild variant="outline">
                        <Link to="/register-org">
                            <Plus data-icon="inline-start" />
                            Register Organization
                        </Link>
                    </Button>
                )}
            </section>

            {(isLeader || officerMemberships.length > 0) && (
                <Card className="border-primary/15 bg-primary/5 shadow-none">
                    <CardContent className="flex flex-col gap-4 p-5 md:flex-row md:items-center md:justify-between">
                        <div className="flex items-center gap-3">
                            <div className="flex size-10 items-center justify-center rounded-lg bg-primary text-primary-foreground">
                                <ShieldCheck />
                            </div>
                            <div>
                                <p className="font-medium">Officer Access</p>
                                <p className="text-sm text-muted-foreground">Manage the organizations where you hold an officer role.</p>
                            </div>
                        </div>
                        <div className="flex flex-wrap gap-2">
                            {isLeader && (
                                <Button asChild size="sm">
                                    <Link to={`/officer/${user.led_org_id}`}>Manage Your Organization</Link>
                                </Button>
                            )}
                            {officerMemberships.map(m => (
                                <Button asChild key={m.id} size="sm" variant="outline">
                                    <Link to={`/officer/${m.organization}`}>{m.organization_name || m.organization_acronym}</Link>
                                </Button>
                            ))}
                        </div>
                    </CardContent>
                </Card>
            )}

            <Tabs value={activeTab} onValueChange={setActiveTab} className="flex flex-col gap-5">
                <TabsList className="w-fit max-w-full overflow-x-auto">
                    {tabItems.map(tab => (
                        <TabsTrigger key={tab.id} value={tab.id}>{tab.label}</TabsTrigger>
                    ))}
                </TabsList>

                <TabsContent value="overview" className="m-0 flex flex-col gap-6">
                    <div className="grid gap-4 md:grid-cols-3">
                        <StatCard title="My Organizations" value={memberships.length} color="maroon" icon={<Building2 />} />
                        <StatCard title="Upcoming Events" value={upcomingEvents.length} color="green" icon={<CalendarDays />} />
                        <StatCard title="Announcements" value={announcements.length} color="yellow" icon={<Bell />} />
                    </div>

                    <div className="grid gap-4 lg:grid-cols-2">
                        <Card className="shadow-none">
                            <CardHeader>
                                <CardTitle>Upcoming Events</CardTitle>
                                <CardDescription>Your next organization activities.</CardDescription>
                            </CardHeader>
                            <CardContent className="flex flex-col gap-3">
                                {upcomingEvents.length === 0 ? (
                                    <Empty className="border">
                                        <EmptyHeader>
                                            <EmptyMedia variant="icon"><CalendarDays /></EmptyMedia>
                                            <EmptyTitle>No upcoming events</EmptyTitle>
                                            <EmptyDescription>Events from your organizations will appear here.</EmptyDescription>
                                        </EmptyHeader>
                                    </Empty>
                                ) : upcomingEvents.slice(0, 5).map(event => (
                                    <div key={event.id} className="flex items-center justify-between gap-4 rounded-lg border p-3">
                                        <div className="min-w-0">
                                            <p className="truncate font-medium">{event.title}</p>
                                            <p className="truncate text-sm text-muted-foreground">{event.organization_acronym} · {event.venue}</p>
                                        </div>
                                        <Badge variant="secondary">{formatDate(event.start_time)}</Badge>
                                    </div>
                                ))}
                            </CardContent>
                        </Card>

                        <Card className="shadow-none">
                            <CardHeader>
                                <CardTitle>Recent Announcements</CardTitle>
                                <CardDescription>Latest posts from organizations and system admins.</CardDescription>
                            </CardHeader>
                            <CardContent className="flex flex-col gap-3">
                                {featuredAnnouncements.length === 0 ? (
                                    <Empty className="border">
                                        <EmptyHeader>
                                            <EmptyMedia variant="icon"><Megaphone /></EmptyMedia>
                                            <EmptyTitle>No announcements</EmptyTitle>
                                            <EmptyDescription>New announcements will appear here.</EmptyDescription>
                                        </EmptyHeader>
                                    </Empty>
                                ) : featuredAnnouncements.map(ann => (
                                    <div key={ann.id} className={cn('rounded-lg border p-3', ann.is_pinned && 'border-amber-200 bg-amber-50/60')}>
                                        <div className="flex items-start justify-between gap-3">
                                            <p className="font-medium">{ann.title}</p>
                                            {ann.is_pinned && <Badge variant="secondary">Pinned</Badge>}
                                        </div>
                                        <p className="mt-1 text-sm text-muted-foreground">{ann.organization_acronym || 'System'} · {formatDate(ann.created_at)}</p>
                                    </div>
                                ))}
                            </CardContent>
                        </Card>
                    </div>
                </TabsContent>

                <TabsContent value="my-orgs" className="m-0 flex flex-col gap-5">
                    {memberships.length === 0 ? (
                        <Empty className="border bg-background">
                            <EmptyHeader>
                                <EmptyMedia variant="icon"><Users /></EmptyMedia>
                                <EmptyTitle>No organizations yet</EmptyTitle>
                                <EmptyDescription>You have not joined any organizations.</EmptyDescription>
                            </EmptyHeader>
                            <Button onClick={() => setActiveTab('browse')}>Browse Organizations</Button>
                        </Empty>
                    ) : (
                        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
                            {memberships.map(m => (
                                <Card key={m.id} className="shadow-none">
                                    <CardContent className="flex flex-col gap-4 p-5">
                                        <div className="flex items-center gap-3">
                                            <div className="flex size-11 items-center justify-center rounded-lg bg-primary/10 font-semibold text-primary">
                                                {m.organization_acronym?.substring(0, 2)}
                                            </div>
                                            <div className="min-w-0">
                                                <p className="truncate font-medium">{m.organization_name}</p>
                                                <Badge variant={m.role === 'officer' ? 'default' : 'secondary'} className="mt-1">
                                                    {m.role} {m.position && `- ${m.position}`}
                                                </Badge>
                                            </div>
                                        </div>
                                        <p className="text-sm text-muted-foreground">Joined {formatDate(m.date_joined)}</p>
                                    </CardContent>
                                </Card>
                            ))}
                        </div>
                    )}
                </TabsContent>

                <TabsContent value="browse" className="m-0">
                    {orgsToJoin.length === 0 ? (
                        <Empty className="border bg-background">
                            <EmptyHeader>
                                <EmptyMedia variant="icon"><Building2 /></EmptyMedia>
                                <EmptyTitle>No available organizations</EmptyTitle>
                                <EmptyDescription>You are already a member of all active organizations, or none are available.</EmptyDescription>
                            </EmptyHeader>
                        </Empty>
                    ) : (
                        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
                            {orgsToJoin.map(org => (
                                <Card key={org.id} className="shadow-none">
                                    <CardContent className="flex flex-col gap-4 p-5">
                                        <div className="flex items-center gap-3">
                                            <div className="flex size-11 items-center justify-center rounded-lg bg-emerald-50 font-semibold text-emerald-700">
                                                {org.acronym?.substring(0, 2)}
                                            </div>
                                            <div className="min-w-0">
                                                <p className="truncate font-medium">{org.name}</p>
                                                <p className="text-sm text-muted-foreground">{org.member_count} members</p>
                                            </div>
                                        </div>
                                        <Button
                                            variant="outline"
                                            onClick={() => {
                                                setSelectedOrg(org);
                                                setShowJoinModal(true);
                                            }}
                                        >
                                            Request to Join
                                        </Button>
                                    </CardContent>
                                </Card>
                            ))}
                        </div>
                    )}
                </TabsContent>

                <TabsContent value="events" className="m-0 flex flex-col gap-4">
                    {upcomingEvents.length === 0 ? (
                        <Empty className="border bg-background">
                            <EmptyHeader>
                                <EmptyMedia variant="icon"><CalendarDays /></EmptyMedia>
                                <EmptyTitle>No upcoming events</EmptyTitle>
                                <EmptyDescription>Events you can attend will appear here.</EmptyDescription>
                            </EmptyHeader>
                        </Empty>
                    ) : upcomingEvents.map(event => (
                        <Card key={event.id} className="shadow-none">
                            <CardContent className="flex flex-col gap-4 p-5 md:flex-row md:items-start md:justify-between">
                                <div>
                                    <p className="text-lg font-medium">{event.title}</p>
                                    <p className="text-sm text-muted-foreground">{event.organization_acronym}</p>
                                    <div className="mt-3 flex flex-wrap gap-3 text-sm text-muted-foreground">
                                        <span className="inline-flex items-center gap-1.5"><MapPin /> {event.venue}</span>
                                        <span className="inline-flex items-center gap-1.5"><CalendarDays /> {new Date(event.start_time).toLocaleString()}</span>
                                    </div>
                                </div>
                                <Badge variant="secondary">{event.attendee_count} attending</Badge>
                            </CardContent>
                        </Card>
                    ))}
                </TabsContent>

                <TabsContent value="announcements" className="m-0 flex flex-col gap-4">
                    {announcements.length === 0 ? (
                        <Empty className="border bg-background">
                            <EmptyHeader>
                                <EmptyMedia variant="icon"><Megaphone /></EmptyMedia>
                                <EmptyTitle>No announcements</EmptyTitle>
                                <EmptyDescription>Organization posts and reminders will appear here.</EmptyDescription>
                            </EmptyHeader>
                        </Empty>
                    ) : announcements.map(ann => (
                        <Card key={ann.id} className={cn('shadow-none', ann.is_pinned && 'border-amber-200')}>
                            <CardContent className="p-5">
                                <div className="flex flex-col gap-3 md:flex-row md:items-start md:justify-between">
                                    <div>
                                        <div className="flex flex-wrap items-center gap-2">
                                            <p className="text-lg font-medium">{ann.title}</p>
                                            {ann.is_pinned && <Badge variant="secondary">Pinned</Badge>}
                                        </div>
                                        <p className="mt-1 text-sm text-muted-foreground">{ann.organization_acronym || 'System Announcement'}</p>
                                        <p className="mt-3 text-sm leading-6 text-foreground/80">{ann.content}</p>
                                    </div>
                                    <span className="text-sm text-muted-foreground">{formatDate(ann.created_at)}</span>
                                </div>
                            </CardContent>
                        </Card>
                    ))}
                </TabsContent>
            </Tabs>

            <Dialog open={showJoinModal} onOpenChange={setShowJoinModal}>
                <DialogContent>
                    <DialogHeader>
                        <DialogTitle>Join {selectedOrg?.name}</DialogTitle>
                        <DialogDescription>Send a short optional note to the organization officers.</DialogDescription>
                    </DialogHeader>
                    <FieldGroup>
                        <Field>
                            <FieldLabel htmlFor="join-message">Message</FieldLabel>
                            <Textarea
                                id="join-message"
                                placeholder="Why do you want to join? (optional)"
                                value={joinMessage}
                                onChange={(e) => setJoinMessage(e.target.value)}
                                rows={4}
                            />
                        </Field>
                    </FieldGroup>
                    <DialogFooter>
                        <Button
                            variant="outline"
                            onClick={() => {
                                setShowJoinModal(false);
                                setSelectedOrg(null);
                            }}
                        >
                            Cancel
                        </Button>
                        <Button onClick={handleJoinRequest}>Send Request</Button>
                    </DialogFooter>
                </DialogContent>
            </Dialog>
        </div>
    );
};

export default StudentDashboard;
