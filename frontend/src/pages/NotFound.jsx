import React from 'react';
import { Link } from 'react-router-dom';
import { Compass } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';

const NotFound = () => {
    return (
        <main className="flex min-h-screen items-center justify-center bg-muted/30 px-4">
            <Card className="w-full max-w-md text-center shadow-sm">
                <CardContent className="flex flex-col items-center p-8">
                    <div className="flex size-12 items-center justify-center rounded-lg bg-primary/10 text-primary">
                        <Compass />
                    </div>
                    <p className="mt-6 text-sm font-medium text-muted-foreground">404</p>
                    <h1 className="mt-2 text-2xl font-semibold tracking-tight">Page Not Found</h1>
                    <p className="mt-2 text-sm leading-6 text-muted-foreground">
                        The page you are looking for does not exist or has been moved.
                    </p>
                    <Button asChild className="mt-6">
                        <Link to="/">Go Back Home</Link>
                    </Button>
                </CardContent>
            </Card>
        </main>
    );
};

export default NotFound;
