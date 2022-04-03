import { Fragment, useMemo, useRef, useState } from 'react';
import {
	AppBar,
	Toolbar,
	Avatar,
	IconButton,
	Menu,
	MenuItem,
	SxProps,
	Theme,
	Box,
	Button,
	Accordion,
	AccordionSummary,
	AccordionDetails,
} from '@mui/material';
import { Menu as MenuIcon, ArrowDropDown, AccountCircle } from '@mui/icons-material';
import { useHistory } from 'react-router';
import { useCheckSessionQuery, useLogoutMutation } from '../api';
import DripDrop from '../images/dripdrop.png';

const NavBar = () => {
	const [openMobileMenu, setOpenMobileMenu] = useState(false);
	const [openYTMenu, setOpenYTMenu] = useState(false);
	const [openUserMenu, setOpenUserMenu] = useState(false);

	const ytMenu = useRef<HTMLButtonElement | null>(null);
	const userMenu = useRef<HTMLButtonElement | null>(null);

	const checkSessionStatus = useCheckSessionQuery(null);
	const [logout] = useLogoutMutation();

	const history = useHistory();

	const CustomMenuItem = ({
		children,
		isMobile = false,
		sx,
		onClick,
	}: {
		children: React.ReactNode;
		sx?: SxProps<Theme>;
		onClick?: () => void;
		isMobile?: boolean;
	}) =>
		useMemo(
			() => (
				<MenuItem
					sx={sx}
					onClick={() => {
						if (isMobile) {
							setOpenMobileMenu(false);
						} else {
							setOpenUserMenu(false);
							setOpenYTMenu(false);
						}
						if (onClick) {
							onClick();
						}
					}}
				>
					{children}
				</MenuItem>
			),
			[children, isMobile, onClick, sx]
		);

	const NavButtons = useMemo(() => {
		if (checkSessionStatus.currentData && checkSessionStatus.isSuccess) {
			return (
				<Fragment>
					<Box display={{ xs: 'none', md: 'contents' }}>
						<Button color="inherit" onClick={() => history.push('/')}>
							Home
						</Button>
						<Button color="inherit" onClick={() => history.push('/music')}>
							Music Downloader
						</Button>
						<Button color="inherit" ref={ytMenu} onClick={() => setOpenYTMenu(true)}>
							Youtube Collections
							<ArrowDropDown />
						</Button>
						<Box flex={1} />
						<IconButton ref={userMenu} onClick={() => setOpenUserMenu(true)}>
							<AccountCircle />
						</IconButton>
					</Box>
					<Menu anchorEl={ytMenu.current} open={openYTMenu} onClose={() => setOpenYTMenu(false)}>
						<CustomMenuItem onClick={() => history.push('/youtube/videos')}>Videos</CustomMenuItem>
						<CustomMenuItem onClick={() => history.push('/youtube/subscriptions')}>Subscriptions</CustomMenuItem>
					</Menu>
					<Menu anchorEl={userMenu.current} open={openUserMenu} onClose={() => setOpenUserMenu(false)}>
						<CustomMenuItem onClick={() => logout(null)}>Logout</CustomMenuItem>
					</Menu>
				</Fragment>
			);
		}
		return null;
	}, [checkSessionStatus.currentData, checkSessionStatus.isSuccess, history, logout, openUserMenu, openYTMenu]);

	const MobileMenu = useMemo(() => {
		if (checkSessionStatus.currentData && checkSessionStatus.isSuccess) {
			return (
				<Accordion expanded={openMobileMenu} sx={{ flexGrow: 1, background: 'transparent' }}>
					<AccordionSummary onClick={() => setOpenMobileMenu(!openMobileMenu)} expandIcon={<MenuIcon />}>
						<Avatar alt="Dripdrop" src={DripDrop} />
					</AccordionSummary>
					<AccordionDetails>
						<CustomMenuItem isMobile onClick={() => history.push('/')}>
							Home
						</CustomMenuItem>
						<CustomMenuItem isMobile onClick={() => history.push('/music')}>
							Music Downloader
						</CustomMenuItem>
						<MenuItem>Youtube Collections</MenuItem>
						<Box marginLeft={1}>
							<CustomMenuItem isMobile onClick={() => history.push('/youtube/videos')}>
								Videos
							</CustomMenuItem>
							<CustomMenuItem isMobile onClick={() => history.push('/youtube/subscriptions')}>
								Subscriptions
							</CustomMenuItem>
						</Box>
						<CustomMenuItem isMobile sx={{ justifyContent: 'space-between' }} onClick={() => logout(null)}>
							<AccountCircle />
							Logout
						</CustomMenuItem>
					</AccordionDetails>
				</Accordion>
			);
		}
		return <Avatar alt="Dripdrop" src={DripDrop} />;
	}, [checkSessionStatus.currentData, checkSessionStatus.isSuccess, history, logout, openMobileMenu]);

	return useMemo(
		() => (
			<Box>
				<Box display={{ xs: 'none', md: 'block' }}>
					<AppBar position="sticky">
						<Toolbar>
							<Avatar alt="Dripdrop" src={DripDrop} />
							{NavButtons}
						</Toolbar>
					</AppBar>
				</Box>
				<Box display={{ md: 'none' }}>
					<AppBar position="sticky">
						<Toolbar disableGutters>{MobileMenu}</Toolbar>
					</AppBar>
				</Box>
			</Box>
		),
		[MobileMenu, NavButtons]
	);
};

export default NavBar;
