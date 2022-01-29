import { Fragment } from 'react';
import { Box } from '@mui/material';
import { useRecoilValueLoadable } from 'recoil';
import { userAtom } from '../../atoms/Auth';
import CustomLink from '../Link';
import YoutubeDropdown from './YoutubeDropdown';
import DripDrop from '../../images/dripdrop.png';
import UserDropdown from './UserDropdown';

const Header = () => {
	const user = useRecoilValueLoadable(userAtom);

	if (user.state === 'hasValue') {
		if (user.getValue()) {
			return (
				<Fragment>
					<CustomLink button={true} to="/" text={<img height="40px" alt="DripDrop" src={DripDrop} />} />
					<CustomLink button={true} to="/music" text="Music Downloader" textColor="white" />
					<YoutubeDropdown />
					<Box sx={{ flexGrow: 1 }} />
					<UserDropdown />
				</Fragment>
			);
		}
	}
	return null;
};

export default Header;
