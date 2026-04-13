import React from 'react';
import Navigation from './Navigation';

const MainLayout = ({ children }) => {
    return (
        <div className="flex">
            <Navigation />
            <main className="flex-1 md:ml-20">
                {children}
            </main>
        </div>
    );
};

export default MainLayout;
