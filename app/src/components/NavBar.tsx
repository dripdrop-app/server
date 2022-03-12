import { Fragment, useEffect, useMemo } from 'react';
import { useRecoilValueLoadable, useSetRecoilState } from 'recoil';
import { Dropdown, Icon, Image, Menu, Sticky } from 'semantic-ui-react';
import { useHistory } from 'react-router';
import { resetUserState, userState } from '../state/Auth';
import DripDrop from '../images/dripdrop.png';
import useLazyFetch from '../hooks/useLazyFetch';

const NavBar = () => {
	const user = useRecoilValueLoadable(userState);
	const history = useHistory();

	const [logout, logoutStatus] = useLazyFetch<null>();
	const resetUser = useSetRecoilState(resetUserState);

	useEffect(() => {
		if (logoutStatus.success) {
			resetUser(null);
		}
	}, [logoutStatus.success, resetUser]);

	const NavButtons = useMemo(() => {
		if (user.state === 'hasValue' && user.contents.authenticated) {
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
								<Dropdown.Item>{user.contents.email}</Dropdown.Item>
								<Dropdown.Item onClick={() => logout({ url: '/auth/logout' })}>Logout</Dropdown.Item>
							</Dropdown.Menu>
						</Dropdown>
					</Menu.Menu>
				</Fragment>
			);
		}
		return null;
	}, [history, logout, user.contents.authenticated, user.contents.email, user.state]);

	return (
		<Sticky>
			<Menu style={{ borderRadius: 0 }} color="blue" inverted borderless stackable>
				<Menu.Item>
					<Image size="mini" src={DripDrop} />
				</Menu.Item>
				{NavButtons}
			</Menu>
		</Sticky>
	);
};

export default NavBar;
