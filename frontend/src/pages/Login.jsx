import React from 'react';
import { Link } from 'react-router-dom';
import { LogIn, ShieldCheck } from 'lucide-react';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Field, FieldError, FieldGroup, FieldLabel } from '@/components/ui/field';
import { Input } from '@/components/ui/input';
import { useLogin } from '../hooks/useLogin';

const Login = () => {
    const {
        email,
        setEmail,
        password,
        setPassword,
        error,
        handleSubmit
    } = useLogin();

    return (
        <main className="flex min-h-screen items-center justify-center bg-muted/30 px-4 py-10">
            <div className="grid w-full min-w-0 max-w-[calc(100vw-2rem)] overflow-hidden rounded-lg border bg-background shadow-sm md:max-w-5xl md:grid-cols-[0.9fr_1.1fr]">
                <section className="hidden border-r bg-muted/40 p-10 md:flex md:flex-col md:justify-between">
                    <div>
                        <div className="flex size-10 items-center justify-center rounded-lg bg-primary text-primary-foreground">
                            <ShieldCheck />
                        </div>
                        <h1 className="mt-6 text-2xl font-semibold tracking-tight">PSU-CMS</h1>
                        <p className="mt-3 max-w-sm text-sm leading-6 text-muted-foreground">
                            Minimal campus operations for organization memberships, events, requests, documents, and budgets.
                        </p>
                    </div>
                    <div className="rounded-lg border bg-background p-4">
                        <p className="text-sm font-medium">Campus access</p>
                        <p className="mt-1 text-sm text-muted-foreground">Use your registered account to continue.</p>
                    </div>
                </section>

                <section className="flex min-w-0 items-center justify-center p-4 md:p-10">
                    <Card className="w-full min-w-0 max-w-full border-0 shadow-none md:max-w-md">
                        <CardHeader className="px-0">
                            <CardTitle className="text-2xl">Welcome back</CardTitle>
                            <CardDescription className="text-pretty">Log in to manage your campus organization workspace.</CardDescription>
                        </CardHeader>
                        <CardContent className="px-0">
                            <form onSubmit={handleSubmit}>
                                <FieldGroup>
                                    <Field>
                                        <FieldLabel htmlFor="email">Email</FieldLabel>
                                        <Input
                                            id="email"
                                            type="email"
                                            placeholder="name@parsu.edu.ph"
                                            value={email}
                                            onChange={(e) => setEmail(e.target.value)}
                                            required
                                        />
                                    </Field>
                                    <Field>
                                        <FieldLabel htmlFor="password">Password</FieldLabel>
                                        <Input
                                            id="password"
                                            type="password"
                                            placeholder="Enter your password"
                                            value={password}
                                            onChange={(e) => setPassword(e.target.value)}
                                            required
                                        />
                                    </Field>
                                    {error && (
                                        <Alert variant="destructive">
                                            <AlertTitle>Login failed</AlertTitle>
                                            <AlertDescription>{error}</AlertDescription>
                                        </Alert>
                                    )}
                                    <Button type="submit" className="w-full">
                                        <LogIn data-icon="inline-start" />
                                        Login
                                    </Button>
                                    <FieldError className="text-center text-muted-foreground">
                                        Don&apos;t have an account?{' '}
                                        <Link to="/signup" className="font-medium text-primary underline-offset-4 hover:underline">
                                            Sign up
                                        </Link>
                                    </FieldError>
                                </FieldGroup>
                            </form>
                        </CardContent>
                    </Card>
                </section>
            </div>
        </main>
    );
};

export default Login;
