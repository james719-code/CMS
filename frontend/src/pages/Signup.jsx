import React from 'react';
import { Link } from 'react-router-dom';
import { UserPlus } from 'lucide-react';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Field, FieldError, FieldGroup, FieldLabel } from '@/components/ui/field';
import { Input } from '@/components/ui/input';
import { useSignup } from '../hooks/useSignup';

const Signup = () => {
    const {
        error,
        handleChange,
        handleSubmit
    } = useSignup();

    return (
        <main className="flex min-h-screen items-center justify-center bg-muted/30 px-4 py-10">
            <Card className="w-full min-w-0 max-w-[calc(100vw-2rem)] shadow-sm md:max-w-xl">
                <CardHeader>
                    <CardTitle>Create your PSU-CMS account</CardTitle>
                    <CardDescription>Register with your campus details to join and manage student organizations.</CardDescription>
                </CardHeader>
                <CardContent>
                    <form onSubmit={handleSubmit}>
                        <FieldGroup>
                            <div className="grid gap-4 md:grid-cols-2">
                                <Field>
                                    <FieldLabel htmlFor="first_name">First Name</FieldLabel>
                                    <Input id="first_name" name="first_name" type="text" placeholder="First name" onChange={handleChange} required />
                                </Field>
                                <Field>
                                    <FieldLabel htmlFor="last_name">Last Name</FieldLabel>
                                    <Input id="last_name" name="last_name" type="text" placeholder="Last name" onChange={handleChange} required />
                                </Field>
                            </div>
                            <Field>
                                <FieldLabel htmlFor="student_id">Student ID</FieldLabel>
                                <Input id="student_id" name="student_id" type="text" placeholder="Student ID" onChange={handleChange} required />
                            </Field>
                            <Field>
                                <FieldLabel htmlFor="signup_email">Email (@parsu.edu.ph)</FieldLabel>
                                <Input id="signup_email" name="email" type="email" placeholder="name@parsu.edu.ph" onChange={handleChange} required />
                            </Field>
                            <Field>
                                <FieldLabel htmlFor="signup_password">Password</FieldLabel>
                                <Input id="signup_password" name="password" type="password" placeholder="Create a password" onChange={handleChange} required />
                            </Field>
                            {error && (
                                <Alert variant="destructive">
                                    <AlertTitle>Sign up failed</AlertTitle>
                                    <AlertDescription>{error}</AlertDescription>
                                </Alert>
                            )}
                            <Button type="submit" className="w-full">
                                <UserPlus data-icon="inline-start" />
                                Sign Up
                            </Button>
                            <FieldError className="text-center text-muted-foreground">
                                Already have an account?{' '}
                                <Link to="/login" className="font-medium text-primary underline-offset-4 hover:underline">
                                    Log in
                                </Link>
                            </FieldError>
                        </FieldGroup>
                    </form>
                </CardContent>
            </Card>
        </main>
    );
};

export default Signup;
