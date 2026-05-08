import React, { useEffect, useMemo, useState } from 'react';
import { Link, Outlet, useLocation, useNavigate } from 'react-router-dom';
import {
    Bell,
    Building2,
    ChevronRight,
    ClipboardList,
    Home,
    LogOut,
    PanelLeft,
    Plus,
    Shield,
    Sparkles,
    UserRound,
} from 'lucide-react';
import { Avatar, AvatarFallback } from '@/components/ui/avatar';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import {
    DropdownMenu,
    DropdownMenuContent,
    DropdownMenuGroup,
    DropdownMenuItem,
    DropdownMenuLabel,
    DropdownMenuSeparator,
    DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import {
    Sidebar,
    SidebarContent,
    SidebarFooter,
    SidebarGroup,
    SidebarGroupContent,
    SidebarGroupLabel,
    SidebarHeader,
    SidebarInset,
    SidebarMenu,
    SidebarMenuButton,
    SidebarMenuItem,
    SidebarProvider,
    SidebarRail,
    SidebarSeparator,
    SidebarTrigger,
} from '@/components/ui/sidebar';
import api from '../api/axios';
import { useAuth } from '../context/AuthContext';

const initialsFor = (user) => {
    const initials = `${user?.first_name?.[0] || ''}${user?.last_name?.[0] || ''}`.trim();
    return initials || user?.email?.[0]?.toUpperCase() || 'U';
};

const Layout = () => {
    const { user, logout } = useAuth();
    const navigate = useNavigate();
    const location = useLocation();
    const [officerOrgs, setOfficerOrgs] = useState([]);

    useEffect(() => {
        const fetchOfficerOrgs = async () => {
            try {
                const res = await api.get('/api/memberships/');
                const myMemberships = res.data.filter(m => m.user === user?.id && m.role === 'officer');
                setOfficerOrgs(myMemberships);
            } catch (err) {
                console.error('Failed to fetch memberships', err);
            }
        };

        if (user) fetchOfficerOrgs();
    }, [user]);

    const handleLogout = () => {
        logout();
        navigate('/login');
    };

    const primaryNav = useMemo(() => {
        const items = [
            user?.is_staff
                ? { to: '/admin', label: 'Admin Dashboard', icon: Shield }
                : { to: '/dashboard', label: 'Dashboard', icon: Home },
        ];

        if (!user?.led_org_id && !user?.is_staff) {
            items.push({ to: '/register-org', label: 'Register Organization', icon: Plus });
        }

        return items;
    }, [user]);

    const officerNav = useMemo(() => {
        const items = [];

        if (user?.led_org_id && user?.led_org_status === 'active') {
            items.push({
                to: `/officer/${user.led_org_id}`,
                label: user.led_org_name || 'My Organization',
                icon: Building2,
            });
        }

        officerOrgs.forEach((membership) => {
            items.push({
                to: `/officer/${membership.organization}`,
                label: membership.organization_acronym || membership.organization_name,
                icon: ClipboardList,
            });
        });

        return items;
    }, [officerOrgs, user]);

    const isActive = (path) => location.pathname === path || location.pathname.startsWith(`${path}/`);

    const NavItem = ({ item }) => {
        const Icon = item.icon;

        return (
            <SidebarMenuItem>
                <SidebarMenuButton asChild isActive={isActive(item.to)} tooltip={item.label}>
                    <Link to={item.to}>
                        <Icon />
                        <span>{item.label}</span>
                    </Link>
                </SidebarMenuButton>
            </SidebarMenuItem>
        );
    };

    return (
        <SidebarProvider>
            <Sidebar collapsible="icon" className="border-sidebar-border bg-sidebar">
                <SidebarHeader className="gap-3 border-b border-sidebar-border p-3">
                    <div className="flex items-center gap-2">
                        <div className="flex size-8 items-center justify-center rounded-lg bg-primary text-primary-foreground">
                            <Sparkles />
                        </div>
                        <div className="min-w-0 group-data-[collapsible=icon]:hidden">
                            <p className="truncate text-sm font-semibold">PSU-CMS</p>
                            <p className="truncate text-xs text-muted-foreground">Club Management</p>
                        </div>
                    </div>
                </SidebarHeader>

                <SidebarContent>
                    <SidebarGroup>
                        <SidebarGroupLabel>Workspace</SidebarGroupLabel>
                        <SidebarGroupContent>
                            <SidebarMenu>
                                {primaryNav.map(item => <NavItem item={item} key={item.to} />)}
                            </SidebarMenu>
                        </SidebarGroupContent>
                    </SidebarGroup>

                    {officerNav.length > 0 && (
                        <>
                            <SidebarSeparator />
                            <SidebarGroup>
                                <SidebarGroupLabel>Officer Access</SidebarGroupLabel>
                                <SidebarGroupContent>
                                    <SidebarMenu>
                                        {officerNav.map(item => <NavItem item={item} key={item.to} />)}
                                    </SidebarMenu>
                                </SidebarGroupContent>
                            </SidebarGroup>
                        </>
                    )}
                </SidebarContent>

                <SidebarFooter className="border-t border-sidebar-border p-3">
                    <DropdownMenu>
                        <DropdownMenuTrigger asChild>
                            <Button variant="ghost" className="h-auto w-full justify-start gap-2 px-2 group-data-[collapsible=icon]:justify-center">
                                <Avatar className="size-8">
                                    <AvatarFallback className="bg-primary/10 text-xs font-semibold text-primary">
                                        {initialsFor(user)}
                                    </AvatarFallback>
                                </Avatar>
                                <span className="min-w-0 text-left group-data-[collapsible=icon]:hidden">
                                    <span className="block truncate text-sm font-medium">
                                        {user?.first_name} {user?.last_name}
                                    </span>
                                    <span className="block truncate text-xs text-muted-foreground">
                                        {user?.is_staff ? 'Administrator' : 'Student'}
                                    </span>
                                </span>
                            </Button>
                        </DropdownMenuTrigger>
                        <DropdownMenuContent side="right" align="end" className="w-56">
                            <DropdownMenuLabel>Account</DropdownMenuLabel>
                            <DropdownMenuSeparator />
                            <DropdownMenuGroup>
                                <DropdownMenuItem disabled>
                                    <UserRound />
                                    {user?.email || 'Current user'}
                                </DropdownMenuItem>
                                <DropdownMenuItem onClick={handleLogout}>
                                    <LogOut />
                                    Logout
                                </DropdownMenuItem>
                            </DropdownMenuGroup>
                        </DropdownMenuContent>
                    </DropdownMenu>
                </SidebarFooter>
                <SidebarRail />
            </Sidebar>

            <SidebarInset className="bg-muted/20">
                <header className="sticky top-0 z-10 flex h-14 items-center justify-between border-b bg-background/95 px-4 backdrop-blur supports-[backdrop-filter]:bg-background/80">
                    <div className="flex items-center gap-2">
                        <SidebarTrigger>
                            <PanelLeft />
                        </SidebarTrigger>
                        <div className="hidden items-center gap-1 text-sm text-muted-foreground md:flex">
                            <span>PSU-CMS</span>
                            <ChevronRight />
                            <span className="font-medium text-foreground">
                                {user?.is_staff ? 'Admin' : 'Workspace'}
                            </span>
                        </div>
                    </div>
                    <div className="flex items-center gap-2">
                        <Badge variant="outline" className="hidden rounded-md md:inline-flex">
                            {user?.is_staff ? 'Administrator' : 'Student'}
                        </Badge>
                        <Button variant="ghost" size="icon-sm" aria-label="Notifications">
                            <Bell />
                        </Button>
                    </div>
                </header>
                <main className="flex-1 p-4 md:p-6 lg:p-8">
                    <div className="mx-auto flex w-full max-w-7xl flex-col gap-6">
                        <Outlet />
                    </div>
                </main>
            </SidebarInset>
        </SidebarProvider>
    );
};

export default Layout;
