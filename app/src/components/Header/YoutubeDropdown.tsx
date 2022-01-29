import React, { useState, useRef } from 'react';
import { Button, Menu, MenuItem } from '@mui/material';
import CustomLink from '../Link';

const YoutubeDropdown = () => {
	const [showMenu, setShowMenu] = useState(false);
	const buttonRef = useRef<HTMLButtonElement | null>(null);

	return (
		<React.Fragment>
			<Button color="inherit" ref={buttonRef} onClick={() => setShowMenu(!showMenu)}>
				Youtube Collections
			</Button>
			<Menu anchorEl={buttonRef.current} open={showMenu} onClose={() => setShowMenu(false)}>
				<CustomLink
					textColor="black"
					to="/youtube/videos"
					text={<MenuItem onClick={() => setShowMenu(false)}>Videos</MenuItem>}
				/>
				<CustomLink
					textColor="black"
					to="/youtube/subscriptions"
					text={<MenuItem onClick={() => setShowMenu(false)}>Subscriptions</MenuItem>}
				/>
			</Menu>
		</React.Fragment>
	);
};

export default YoutubeDropdown;
