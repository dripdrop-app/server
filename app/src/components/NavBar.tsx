import { Fragment, useCallback, useMemo, useRef, useState } from 'react';
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
	useTheme,
	useMediaQuery,
} from '@mui/material';
import { Menu as MenuIcon, ArrowDropDown, AccountCircle } from '@mui/icons-material';
import { useHistory } from 'react-router';
import { useLogoutMutation } from '../api/auth';
import AuthWrapper from './Auth/AuthWrapper';
import DripDrop from '../images/dripdrop.png';

const NavBar = () => {
	const [openMobileMenu, setOpenMobileMenu] = useState(false);
	const [openYTMenu, setOpenYTMenu] = useState(false);
	const [openUserMenu, setOpenUserMenu] = useState(false);

	const ytMenu = useRef<HTMLButtonElement | null>(null);
	const userMenu = useRef<HTMLButtonElement | null>(null);

	const theme = useTheme();
	const isSmall = useMediaQuery(theme.breakpoints.down('md'));

	const [logout] = useLogoutMutation();

	const history = useHistory();

	const CustomMenuItem = useCallback(
		({ children, sx, onClick }: { children: React.ReactNode; sx?: SxProps<Theme>; onClick?: () => void }) => (
			<MenuItem
				sx={sx}
				onClick={() => {
					if (isSmall) {
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
		[isSmall]
	);

	const NavButtons = useMemo(
		() => (
			<Fragment>
				<Button color="inherit" onClick={() => history.push('/')}>
					Home
				</Button>
				<Button color="inherit" onClick={() => history.push('/music')}>
					Music Downloader
				</Button>
				<Button color="inherit" ref={ytMenu} onClick={() => setOpenYTMenu(true)}>
					Youtube
					<ArrowDropDown />
				</Button>
				<Box flex={1} />
				<IconButton ref={userMenu} onClick={() => setOpenUserMenu(true)}>
					<AccountCircle />
				</IconButton>
				<Menu anchorEl={ytMenu.current} open={openYTMenu} onClose={() => setOpenYTMenu(false)}>
					<CustomMenuItem onClick={() => history.push('/youtube/videos')}>Videos</CustomMenuItem>
					<CustomMenuItem onClick={() => history.push('/youtube/subscriptions')}>Subscriptions</CustomMenuItem>
					<CustomMenuItem onClick={() => history.push('/youtube/videos/queue')}>Video Queue</CustomMenuItem>
				</Menu>
				<Menu anchorEl={userMenu.current} open={openUserMenu} onClose={() => setOpenUserMenu(false)}>
					<CustomMenuItem onClick={() => logout()}>Logout</CustomMenuItem>
				</Menu>
			</Fragment>
		),
		[CustomMenuItem, history, logout, openUserMenu, openYTMenu]
	);

	const MobileMenu = useMemo(
		() => (
			<Accordion expanded={openMobileMenu} sx={{ flexGrow: 1, background: 'transparent' }}>
				<AccordionSummary onClick={() => setOpenMobileMenu(!openMobileMenu)} expandIcon={<MenuIcon />}>
					<Avatar alt="Dripdrop" src={DripDrop} />
				</AccordionSummary>
				<AccordionDetails>
					<CustomMenuItem onClick={() => history.push('/')}>Home</CustomMenuItem>
					<CustomMenuItem onClick={() => history.push('/music')}>Music Downloader</CustomMenuItem>
					<MenuItem>Youtube</MenuItem>
					<Box marginLeft={1}>
						<CustomMenuItem onClick={() => history.push('/youtube/videos')}>Videos</CustomMenuItem>
						<CustomMenuItem onClick={() => history.push('/youtube/subscriptions')}>Subscriptions</CustomMenuItem>
						<CustomMenuItem onClick={() => history.push('/youtube/videos/queue')}>Video Queue</CustomMenuItem>
					</Box>
					<CustomMenuItem sx={{ justifyContent: 'space-between' }} onClick={() => logout()}>
						<AccountCircle />
						Logout
					</CustomMenuItem>
				</AccordionDetails>
			</Accordion>
		),
		[CustomMenuItem, history, logout, openMobileMenu]
	);

	return useMemo(
		() => (
			<AppBar position="sticky">
				<Box display={{ xs: 'none', md: 'contents' }}>
					<Toolbar>
						<Avatar alt="Dripdrop" src={DripDrop} />
						<AuthWrapper>{NavButtons}</AuthWrapper>
					</Toolbar>
				</Box>
				<Box display={{ md: 'none' }}>
					<AuthWrapper altRender={<Avatar alt="Dripdrop" src={DripDrop} />}>
						<Toolbar disableGutters>{MobileMenu}</Toolbar>
					</AuthWrapper>
				</Box>
			</AppBar>
		),
		[MobileMenu, NavButtons]
	);
};

export default NavBar;
