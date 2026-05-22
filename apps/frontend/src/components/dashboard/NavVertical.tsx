import {
  IconHome2,
  IconUsers,
  IconUser,
  IconLock,
  IconWind
} from "@tabler/icons-react";

interface NavVerticalProps {
  activePath: string;
}

const NavVertical = ({ activePath }: NavVerticalProps) => {
  const activeClass =
    "group flex items-center rounded-md px-3 py-2 text-sm font-medium text-slate-800 hover:bg-slate-100 bg-slate-200 mb-1";
  const inactiveClass =
    "group flex items-center rounded-md px-3 py-2 text-sm font-medium text-slate-800 hover:bg-slate-100 transparent mb-1";

  const navItems = [
    { label: "Dashboard", href: "/", icon: IconHome2 },
    { label: "Clients", href: "/clients", icon: IconUsers },
    { label: "Tunnels", href: "/tunnels", icon: IconWind },
    { label: "Admin", href: "/admin", icon: IconLock, adminOnly: true },
    { label: "Profile", href: "/profile", icon: IconUser },
  ];

  return (
    <nav className="grid items-start gap-2">
      <div>
        {navItems.map((item) => (
          <a
            key={item.href}
            href={item.href}
            className={activePath === item.href ? activeClass : inactiveClass}
            id={item.adminOnly ? "admin-nav-link" : undefined}
            style={item.adminOnly ? { display: 'none' } : {}}
          >
            <item.icon className="mr-2" size={20} />
            <span>{item.label}</span>
          </a>
        ))}
      </div>
    </nav>
  );
};

export default NavVertical;
