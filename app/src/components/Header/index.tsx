import { Box, Typography, Button } from '@mui/material';
import React, { Fragment, useEffect } from 'react';
import { useRecoilValueLoadable, useSetRecoilState } from 'recoil';
import { userAtom } from '../../atoms/Auth';
import useLazyFetch from '../../hooks/useLazyFetch';
import CustomLink from '../Link';
import YoutubeDropdown from './YoutubeDropdown';
import DripDrop from '../../images/dripdrop.png';

const Header = () => {
	const user = useRecoilValueLoadable(userAtom);
	const setUser = useSetRecoilState(userAtom);
	const [logout, logoutStatus] = useLazyFetch<null>();

	useEffect(() => {
		if (logoutStatus.isSuccess) {
			setUser(() => null);
		}
	}, [logoutStatus.isSuccess, setUser]);

	if (user.state === 'hasValue') {
		const email = user.getValue()?.email;
		if (email) {
			return (
				<Fragment>
					<CustomLink button={true} to="/" text={<img height="40px" alt="DripDrop" src={DripDrop} />} />
					<CustomLink button={true} to="/music" text="Music Downloader" />
					<YoutubeDropdown />
					<Box sx={{ flexGrow: 1 }} />
					<Typography variant="h5">{email}</Typography>
					<Button onClick={() => logout({ url: '/auth/logout' })} color="inherit">
						Logout
					</Button>
				</Fragment>
			);
		}
	}
	return null;
};

export default Header;
