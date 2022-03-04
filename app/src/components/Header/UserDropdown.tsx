import React, { useEffect, useRef, useState } from 'react';
import { useRecoilValue, useSetRecoilState } from 'recoil';
import { Button, Avatar, Menu, MenuItem } from '@mui/material';
import { Person } from '@mui/icons-material';
import { userState, resetUserState } from '../../state/Auth';
import useLazyFetch from '../../hooks/useLazyFetch';

const UserDropdown = () => {
	const [showMenu, setShowMenu] = useState(false);
	const buttonRef = useRef<null | HTMLButtonElement>(null);
	const user = useRecoilValue(userState);
	const resetUser = useSetRecoilState(resetUserState);

	const [logout, logoutStatus] = useLazyFetch<null>();

	useEffect(() => {
		if (logoutStatus.success) {
			resetUser(null);
		}
	}, [logoutStatus.success, resetUser]);

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
