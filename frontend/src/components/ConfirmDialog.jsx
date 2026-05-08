import React from 'react';
import { AlertTriangle, CheckCircle2, CircleHelp } from 'lucide-react';
import {
    AlertDialog,
    AlertDialogAction,
    AlertDialogCancel,
    AlertDialogContent,
    AlertDialogDescription,
    AlertDialogFooter,
    AlertDialogHeader,
    AlertDialogTitle,
} from '@/components/ui/alert-dialog';
import { cn } from '@/lib/utils';

const variantConfig = {
    danger: {
        icon: AlertTriangle,
        iconClass: 'bg-destructive/10 text-destructive',
        actionClass: 'bg-destructive text-white hover:bg-destructive/90',
    },
    warning: {
        icon: AlertTriangle,
        iconClass: 'bg-amber-50 text-amber-700',
        actionClass: 'bg-amber-600 text-white hover:bg-amber-700',
    },
    success: {
        icon: CheckCircle2,
        iconClass: 'bg-emerald-50 text-emerald-700',
        actionClass: 'bg-emerald-700 text-white hover:bg-emerald-800',
    },
    primary: {
        icon: CircleHelp,
        iconClass: 'bg-primary/10 text-primary',
        actionClass: 'bg-primary text-primary-foreground hover:bg-primary/90',
    },
};

const ConfirmDialog = ({
    isOpen,
    onClose,
    onConfirm,
    title,
    message,
    confirmText = 'Confirm',
    cancelText = 'Cancel',
    variant = 'danger',
}) => {
    const config = variantConfig[variant] || variantConfig.primary;
    const Icon = config.icon;

    return (
        <AlertDialog open={isOpen} onOpenChange={(open) => !open && onClose()}>
            <AlertDialogContent>
                <AlertDialogHeader>
                    <div className={cn('mb-2 flex size-10 items-center justify-center rounded-lg', config.iconClass)}>
                        <Icon />
                    </div>
                    <AlertDialogTitle>{title}</AlertDialogTitle>
                    <AlertDialogDescription>{message}</AlertDialogDescription>
                </AlertDialogHeader>
                <AlertDialogFooter>
                    <AlertDialogCancel>{cancelText}</AlertDialogCancel>
                    <AlertDialogAction
                        className={config.actionClass}
                        onClick={() => {
                            onConfirm();
                            onClose();
                        }}
                    >
                        {confirmText}
                    </AlertDialogAction>
                </AlertDialogFooter>
            </AlertDialogContent>
        </AlertDialog>
    );
};

export default ConfirmDialog;
