import React from 'react';
import { ClipboardCheck } from 'lucide-react';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Field, FieldGroup, FieldLabel } from '@/components/ui/field';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { useOrgRegistration } from '../hooks/useOrgRegistration';

const OrgRegistration = () => {
    const {
        error,
        handleChange,
        handleSubmit
    } = useOrgRegistration();

    return (
        <div className="grid gap-6 lg:grid-cols-[0.75fr_1.25fr]">
            <section>
                <p className="text-sm font-medium text-primary">Organization application</p>
                <h1 className="mt-2 text-3xl font-semibold tracking-tight">Register New Organization</h1>
                <p className="mt-2 max-w-xl text-sm leading-6 text-muted-foreground">
                    Submit the core identity, mission, and vision details for administrator review.
                </p>
            </section>
            <Card className="shadow-none">
                <CardHeader>
                    <CardTitle>Application details</CardTitle>
                    <CardDescription>Use clear names and concise statements for faster approval.</CardDescription>
                </CardHeader>
                <CardContent>
                    {error && (
                        <Alert variant="destructive" className="mb-5">
                            <AlertTitle>Unable to submit application</AlertTitle>
                            <AlertDescription>{error}</AlertDescription>
                        </Alert>
                    )}
                    <form onSubmit={handleSubmit}>
                        <FieldGroup>
                            <div className="grid gap-4 md:grid-cols-[1fr_0.45fr]">
                                <Field>
                                    <FieldLabel htmlFor="org_name">Organization Name</FieldLabel>
                                    <Input id="org_name" name="name" onChange={handleChange} required />
                                </Field>
                                <Field>
                                    <FieldLabel htmlFor="org_acronym">Acronym</FieldLabel>
                                    <Input id="org_acronym" name="acronym" onChange={handleChange} required />
                                </Field>
                            </div>
                            <Field>
                                <FieldLabel htmlFor="description">Description</FieldLabel>
                                <Textarea id="description" name="description" onChange={handleChange} rows={3} />
                            </Field>
                            <Field>
                                <FieldLabel htmlFor="mission">Mission</FieldLabel>
                                <Textarea id="mission" name="mission" onChange={handleChange} rows={3} />
                            </Field>
                            <Field>
                                <FieldLabel htmlFor="vision">Vision</FieldLabel>
                                <Textarea id="vision" name="vision" onChange={handleChange} rows={3} />
                            </Field>
                            <Button type="submit" className="w-full">
                                <ClipboardCheck data-icon="inline-start" />
                                Submit Application
                            </Button>
                        </FieldGroup>
                    </form>
                </CardContent>
            </Card>
        </div>
    );
};

export default OrgRegistration;
