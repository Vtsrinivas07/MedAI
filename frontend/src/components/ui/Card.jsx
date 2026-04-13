import React from 'react';
import { motion } from 'framer-motion';

const Card = ({
    children,
    className = '',
    hover = false,
    onClick,
    ...props
}) => {
    const baseClasses = 'bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded-lg shadow-sm';
    const hoverClasses = hover ? 'cursor-pointer transition-all duration-200 hover:shadow-md hover:border-gray-400 dark:hover:border-gray-500' : '';

    const cardClasses = `${baseClasses} ${hoverClasses} ${className}`;

    if (hover || onClick) {
        return (
            <motion.div
                className={cardClasses}
                onClick={onClick}
                whileHover={{ scale: 1.01, y: -2 }}
                whileTap={{ scale: 0.99 }}
                transition={{ type: 'spring', stiffness: 300, damping: 20 }}
                {...props}
            >
                {children}
            </motion.div>
        );
    }

    return (
        <div className={cardClasses} {...props}>
            {children}
        </div>
    );
};

export const CardHeader = ({ children, className = '' }) => (
    <div className={`px-6 py-4 border-b border-gray-300 dark:border-gray-600 ${className}`}>
        {children}
    </div>
);

export const CardBody = ({ children, className = '' }) => (
    <div className={`px-6 py-4 ${className}`}>
        {children}
    </div>
);

export const CardFooter = ({ children, className = '' }) => (
    <div className={`px-6 py-4 border-t border-neutral-200 ${className}`}>
        {children}
    </div>
);

export default Card;
