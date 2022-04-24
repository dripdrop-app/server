import { useMemo } from 'react';
import { useCheckYoutubeAuthQuery } from '../../api';

interface YoutubeWrapperProps {
	render: (user: YoutubeAuthState) => JSX.Element;
	altRender?: JSX.Element;
}

const YoutubeWrapper = (props: YoutubeWrapperProps) => {
	const youtubeAuthStatus = useCheckYoutubeAuthQuery();

	return useMemo(() => {
		if (
			youtubeAuthStatus.isSuccess &&
			youtubeAuthStatus.currentData &&
			youtubeAuthStatus.currentData.email &&
			!(process.env.NODE_ENV === 'development' ? false : youtubeAuthStatus.currentData.refresh)
		) {
			return props.render(youtubeAuthStatus.currentData);
		}
		return props.altRender ?? null;
	}, [props, youtubeAuthStatus.currentData, youtubeAuthStatus.isSuccess]);
};

export default YoutubeWrapper;
