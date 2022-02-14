import React, { useEffect, useRef, useState } from 'react';
import { Button, Avatar, Menu, MenuItem } from '@mui/material';
import { Person } from '@mui/icons-material';
import { useRecoilState } from 'recoil';
import { initialUserState, userState } from '../../state/Auth';
import useLazyFetch from '../../hooks/useLazyFetch';

const UserDropdown = () => {
	const [user, setUser] = useRecoilState(userState);
	const [showMenu, setShowMenu] = useState(false);
	const buttonRef = useRef<null | HTMLButtonElement>(null);

	const [logout, logoutStatus] = useLazyFetch<null>();

	useEffect(() => {
		if (logoutStatus.isSuccess) {
			setUser(() => initialUserState);
		}
	}, [logoutStatus.isSuccess, setUser]);

	if (user.authenticated) {
		return (
			<React.Fragment>
				<Button ref={buttonRef} onClick={() => setShowMenu(!showMenu)}>
					<Avatar>
						<Person />
					</Avatar>
				</Button>
				<Menu anchorEl={buttonRef.current} open={showMenu} onClose={() => setShowMenu(false)}>
					<MenuItem onClick={() => logout({ url: '/auth/logout' })}>Logout</MenuItem>
				</Menu>
			</React.Fragment>
		);
	}
	return null;
};

export default UserDropdown;
