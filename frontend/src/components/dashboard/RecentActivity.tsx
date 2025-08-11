import React from 'react';

interface Activity {
  id: number;
  type: string;
  message: string;
  time: string;
  icon: React.ComponentType<React.SVGProps<SVGSVGElement>>;
  iconColor: string;
}

interface RecentActivityProps {
  activities: Activity[];
}

export default function RecentActivity({ activities }: RecentActivityProps) {
  return (
    <div className="flow-root">
      <ul role="list" className="-mb-8">
        {activities.map((activity, activityIdx) => (
          <li key={activity.id}>
            <div className="relative pb-8">
              {activityIdx !== activities.length - 1 ? (
                <span
                  className="absolute left-5 top-5 -ml-px h-full w-0.5 bg-gray-200"
                  aria-hidden="true"
                />
              ) : null}
              <div className="relative flex items-start space-x-3">
                <div className="relative">
                  <div className="flex h-10 w-10 items-center justify-center rounded-full bg-gray-100 ring-8 ring-white">
                    <activity.icon 
                      className={`h-5 w-5 ${activity.iconColor}`} 
                      aria-hidden="true" 
                    />
                  </div>
                </div>
                <div className="min-w-0 flex-1">
                  <div>
                    <div className="text-sm">
                      <span className="font-medium text-gray-900">
                        {activity.message}
                      </span>
                    </div>
                    <p className="mt-0.5 text-sm text-gray-500">
                      {activity.time}
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </li>
        ))}
      </ul>
      
      {activities.length === 0 && (
        <div className="text-center py-6">
          <p className="text-sm text-gray-500">
            Henüz aktivite bulunmuyor
          </p>
        </div>
      )}
      
      <div className="mt-6">
        <button className="text-sm text-primary-600 hover:text-primary-700 font-medium">
          Tüm aktiviteleri görüntüle →
        </button>
      </div>
    </div>
  );
}


