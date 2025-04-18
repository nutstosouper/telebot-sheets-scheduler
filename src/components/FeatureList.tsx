
import { Check } from "lucide-react";

const FeatureList = () => {
  const features = [
    {
      title: "Role-Based Access Control",
      description: "Different access levels for clients, administrators, and CEO"
    },
    {
      title: "Google Sheets Integration",
      description: "Store all data in Google Sheets for easy management"
    },
    {
      title: "Client Booking",
      description: "Clients can book appointments and manage their bookings"
    },
    {
      title: "Service Management",
      description: "Admins can add, update, and remove services"
    },
    {
      title: "Statistics & Reporting",
      description: "View booking history and analyze performance"
    },
    {
      title: "Extensible Architecture",
      description: "Designed for future integration with AI tools and analytics"
    }
  ];

  return (
    <ul className="space-y-3">
      {features.map((feature, index) => (
        <li key={index} className="flex">
          <Check className="h-5 w-5 mr-2 text-green-500 flex-shrink-0 mt-0.5" />
          <div>
            <span className="font-medium">{feature.title}</span>
            <p className="text-sm text-gray-600">{feature.description}</p>
          </div>
        </li>
      ))}
    </ul>
  );
};

export default FeatureList;
