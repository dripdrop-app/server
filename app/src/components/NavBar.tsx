import { Fragment, useMemo } from 'react';
import { Dropdown, Icon, Image, Menu } from 'semantic-ui-react';
import { useHistory } from 'react-router';
import { useCheckSessionQuery, useLogoutMutation } from '../api';
import DripDrop from '../images/dripdrop.png';

const NavBar = () => {
	const checkSessionStatus = useCheckSessionQuery(null);
	const [logout] = useLogoutMutation();

	const history = useHistory();

	const NavButtons = useMemo(() => {
		if (checkSessionStatus.currentData && checkSessionStatus.isSuccess) {
			return (
				<Fragment>
					<Menu.Item onClick={() => history.push('/')}>HOME</Menu.Item>
					<Menu.Item onClick={() => history.push('/music')}>MUSIC DOWNLOADER</Menu.Item>
					<Menu.Menu>
						<Dropdown item text="YOUTUBE COLLECTIONS">
							<Dropdown.Menu>
								<Dropdown.Item onClick={() => history.push('/youtube/videos')}>Videos</Dropdown.Item>
								<Dropdown.Item onClick={() => history.push('/youtube/subscriptions')}>Subscriptions</Dropdown.Item>
							</Dropdown.Menu>
						</Dropdown>
					</Menu.Menu>
					<Menu.Menu position="right">
						<Dropdown trigger={<Icon size="big" name="user circle" />} item>
							<Dropdown.Menu>
								<Dropdown.Item>{checkSessionStatus.currentData.email}</Dropdown.Item>
								<Dropdown.Item onClick={() => logout(null)}>Logout</Dropdown.Item>
							</Dropdown.Menu>
						</Dropdown>
					</Menu.Menu>
				</Fragment>
			);
		}
		return null;
	}, [checkSessionStatus.currentData, checkSessionStatus.isSuccess, history, logout]);

	return useMemo(
		() => (
			<Menu style={{ borderRadius: 0 }} color="blue" inverted borderless stackable>
				<Menu.Item>
					<Image size="mini" src={DripDrop} />
				</Menu.Item>
				{NavButtons}
			</Menu>
		),
		[NavButtons]
	);
};

export default NavBar;
