import { Fragment } from 'react';
import { AppBar, Box, Toolbar } from '@mui/material';
import { useRecoilValueLoadable } from 'recoil';
import { userState } from '../../state/Auth';
import CustomLink from '../Link';
import YoutubeDropdown from './YoutubeDropdown';
import DripDrop from '../../images/dripdrop.png';
import UserDropdown from './UserDropdown';

const Header = () => {
	const user = useRecoilValueLoadable(userState);

	return (
		<AppBar position="sticky">
			<Toolbar>
				{user.state === 'hasValue' && user.contents.authenticated ? (
					<Fragment>
						<CustomLink button={true} to="/" text={<img height="40px" alt="DripDrop" src={DripDrop} />} />
						<CustomLink button={true} to="/music" text="Music Downloader" textColor="white" />
						<YoutubeDropdown />
						<Box sx={{ flexGrow: 1 }} />
						<UserDropdown />
					</Fragment>
				) : null}
			</Toolbar>
		</AppBar>
	);
};

export default Header;
