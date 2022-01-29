import { useRecoilState } from 'recoil';
import { Container } from '@mui/material';
import { videosAtom } from '../../atoms/YoutubeCollections';
import FiltersView from './FiltersView';
import CustomGrid from './CustomGrid';
import YoutubeVideoCard from './YoutubeVideoCard';

const VideosView = (props: { channelID: string | null }) => {
	const [videosView, setVideosView] = useRecoilState(videosAtom(props.channelID));
	const { videos } = videosView;

	return (
		<Container sx={{ my: 5 }}>
			<FiltersView state={videosView} updateState={setVideosView}>
				<CustomGrid
					items={videos}
					renderItem={(video, selected) => <YoutubeVideoCard selected={selected} video={video} />}
				/>
			</FiltersView>
		</Container>
	);
};

export default VideosView;
