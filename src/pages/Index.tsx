
import { useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import BotSetup from "@/components/BotSetup";
import GoogleSheetsSetup from "@/components/GoogleSheetsSetup";
import CodePreview from "@/components/CodePreview";
import FeatureList from "@/components/FeatureList";

const Index = () => {
  const [activeTab, setActiveTab] = useState("overview");

  return (
    <div className="min-h-screen bg-gradient-to-b from-blue-50 to-white">
      <header className="bg-white shadow-sm py-6">
        <div className="container mx-auto px-4">
          <h1 className="text-3xl font-bold text-blue-700">TeleBot Scheduler</h1>
          <p className="text-gray-600 mt-2">Telegram Bot with Google Sheets Integration</p>
        </div>
      </header>

      <main className="container mx-auto px-4 py-8">
        <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
          <TabsList className="grid w-full grid-cols-4 mb-8">
            <TabsTrigger value="overview">Overview</TabsTrigger>
            <TabsTrigger value="bot-setup">Bot Setup</TabsTrigger>
            <TabsTrigger value="sheets-setup">Google Sheets</TabsTrigger>
            <TabsTrigger value="code">Code Preview</TabsTrigger>
          </TabsList>

          <TabsContent value="overview" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>Project Overview</CardTitle>
                <CardDescription>
                  A Telegram bot backend solution with Google Sheets integration
                </CardDescription>
              </CardHeader>
              <CardContent>
                <p className="text-gray-700 mb-4">
                  This project implements a backend for a Telegram bot that manages appointments, services, and user roles.
                  All data is stored in Google Sheets, making it easy to manage without a complex database setup.
                </p>
                <h3 className="font-semibold text-lg mb-2">Key Features:</h3>
                <FeatureList />
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="bot-setup">
            <BotSetup />
          </TabsContent>

          <TabsContent value="sheets-setup">
            <GoogleSheetsSetup />
          </TabsContent>

          <TabsContent value="code">
            <CodePreview />
          </TabsContent>
        </Tabs>
      </main>

      <footer className="bg-gray-50 border-t py-6 mt-12">
        <div className="container mx-auto px-4 text-center text-gray-600">
          <p>© 2025 TeleBot Scheduler - A Telegram Bot with Google Sheets Integration</p>
        </div>
      </footer>
    </div>
  );
};

export default Index;
