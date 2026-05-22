import AccountNav from "./AccountNav";

const Header = () => {
  return (
    <header className="sticky top-0 z-40 bg-white px-4">
      <div className="flex h-16 items-center justify-between border-b border-b-slate-200 py-4">
        <div className="flex gap-6 md:gap-10">
          <a
            className="hidden items-center space-x-2 md:flex"
            href="/"
          >
            <span className="inline-grid h-7 w-7 place-items-center rounded-md bg-slate-900 text-xs font-bold text-white">K</span>
            <span className="hidden font-bold sm:inline-block">KannnHole Dashboard</span>
          </a>
        </div>
        <AccountNav />
      </div>
    </header>
  );
};

export default Header;
