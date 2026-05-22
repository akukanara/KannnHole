import * as DropdownMenu from "@radix-ui/react-dropdown-menu";
import {
  HamburgerMenuIcon,
} from "@radix-ui/react-icons";
import "../../styles/dashboard.css";

const AccountNav = () => {
  return (
    <DropdownMenu.Root>
      <DropdownMenu.Trigger asChild>
        <button className="IconButton" aria-label="Customise options">
          <HamburgerMenuIcon />
        </button>
      </DropdownMenu.Trigger>

      <DropdownMenu.Portal>
        <DropdownMenu.Content className="DropdownMenuContent" sideOffset={5}>
          <DropdownMenu.Label className="DropdownMenuLabel">
            Account Settings
          </DropdownMenu.Label>
          <a href="/profile">
            <DropdownMenu.Item className="DropdownMenuItem">
              Profile
            </DropdownMenu.Item>
          </a>
          <DropdownMenu.Separator className="DropdownMenuSeparator" />
          <a href="/logout">
            <DropdownMenu.Item className="DropdownMenuItem">
              Logout
            </DropdownMenu.Item>
          </a>
          <DropdownMenu.Arrow className="DropdownMenuArrow" style={{ fill: 'white' }} />
        </DropdownMenu.Content>
      </DropdownMenu.Portal>
    </DropdownMenu.Root>
  );
};

export default AccountNav;
